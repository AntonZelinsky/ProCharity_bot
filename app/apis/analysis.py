from flask import jsonify, make_response
from flask_apispec import doc
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from sqlalchemy.sql import func

from app.models import ReasonCanceling, Statistics, User
from app.database import db_session
from datetime import datetime, timedelta

from bot.constants import REASONS


class Analysis(MethodResource, Resource):
    @doc(description='Analysis statistics',
         tags=['Analysis']
         )
    @jwt_required()
    def get(self):
        users = (db_session.query(User.has_mailing).all())
        num_users = len(users)
        subscribed_users = len([user for user in users if user['has_mailing']])
        not_subscribed_users = num_users - subscribed_users
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
        return make_response(jsonify(added_users=users_created_date(),
                                     subscribed_users=subscribed_users,
                                     not_subscribed_users=not_subscribed_users,
                                     command_stats=dict(command_stats),
                                     reasons_canceling=dict(reasons_canceling)), 200)


def users_created_date():
    today = datetime.now().date()
    date_begin = today - timedelta(days=30)
    added_users = dict(
        db_session.query(
            func.to_char(User.date_registration, 'YYYY-MM-DD'),
            func.count(User.date_registration)
        ).filter(User.date_registration > date_begin).group_by(
            func.to_char(User.date_registration, 'YYYY-MM-DD')
        ).all()
    )
    return {
        (date_begin + timedelta(days=n)).strftime('%Y-%m-%d'):
            added_users.get((date_begin + timedelta(days=n)).strftime(
                '%Y-%m-%d'
            ), 0) for n in range(1, 31)
    }
