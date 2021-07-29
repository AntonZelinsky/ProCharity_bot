from flask import jsonify, make_response
from sqlalchemy.sql.schema import Column
from flask_apispec import doc
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from sqlalchemy.sql import func

from app.models import ReasonCanceling, Statistics, User
from app.database import db_session
from datetime import datetime, timedelta

from bot.constants import REASONS


class Analytics(MethodResource, Resource):
    @doc(description='Analytics statistics',
         tags=['Analytics']
         )
    @jwt_required()
    def get(self):
        users = db_session.query(User.has_mailing).all()
        number_users = len(users)
        number_subscribed_users = len([user for user in users if user['has_mailing']])
        number_not_subscribed_users = number_users - number_subscribed_users
        command_stats = db_session.query(
            Statistics.command, func.count(Statistics.command)
        ).group_by(Statistics.command).all()
        reasons_canceling_from_db = db_session.query(
            ReasonCanceling.reason_canceling,
            func.count(ReasonCanceling.reason_canceling)
        ).group_by(ReasonCanceling.reason_canceling).all()
        reasons_canceling = {
            REASONS.get(key, 'Другое'):
                value for key, value in reasons_canceling_from_db
        }
        return make_response(jsonify(added_users=get_statistics(User.date_registration),
                                     number_subscribed_users=number_subscribed_users,
                                     number_not_subscribed_users=number_not_subscribed_users,
                                     command_stats=dict(command_stats),
                                     reasons_canceling=dict(reasons_canceling),
                                     users_unsubscribed = get_statistics(ReasonCanceling.added_date)), 200)
    

def get_statistics(column_name:Column) -> dict:
    today = datetime.now().date()
    date_begin = today - timedelta(days=30)
    result = dict(
        db_session.query(
            func.to_char(column_name, 'YYYY-MM-DD'),
            func.count(column_name)
            ).filter(column_name > date_begin
            ).group_by(func.to_char(column_name, 'YYYY-MM-DD')
        ).all())
    
    return {
        (date_begin + timedelta(days=n)).strftime('%Y-%m-%d'):
            result.get((date_begin + timedelta(days=n)).strftime(
                '%Y-%m-%d'
            ), 0) for n in range(1, 31)
    }
