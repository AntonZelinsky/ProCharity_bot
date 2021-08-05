from flask import jsonify, make_response
from sqlalchemy import distinct
from sqlalchemy.sql.schema import Column
from flask_apispec import doc
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from sqlalchemy.sql import func

from app.models import ReasonCanceling, Statistics, User
from app.database import db_session
from datetime import datetime, timedelta

from bot.constants import constants


class Analytics(MethodResource, Resource):
    @doc(description='Analytics statistics',
         tags=['Analytics'])
    @jwt_required()
    def get(self):
        users = db_session.query(User.has_mailing).all()
        number_users = len(users)
        number_subscribed_users = len([user for user in users if user['has_mailing']])
        number_not_subscribed_users = number_users - number_subscribed_users              
        
        reasons_canceling_from_db = get_statistics(ReasonCanceling.reason_canceling)       
        reasons_canceling = {
            constants.REASONS.get(key, 'Другое'):
                value for key, value in reasons_canceling_from_db
        }
        return make_response(jsonify(added_users=get_statistics_by_days(User.date_registration),
                                     added_external_users=get_statistics_by_days(User.external_signup_date),
                                     number_subscribed_users=number_subscribed_users,
                                     number_not_subscribed_users=number_not_subscribed_users,
                                     command_stats=dict(get_statistics(Statistics.command)),
                                     reasons_canceling=reasons_canceling,
                                     users_unsubscribed = get_statistics_by_days(ReasonCanceling.added_date),
                                     distinct_users_unsubscribed = get_statistics_by_days(
                                         ReasonCanceling.added_date, ReasonCanceling.telegram_id),
                                     active_users = get_statistics_by_days(Statistics.added_date, Statistics.telegram_id),
                                     active_users_per_month = get_monthly_statistics(
                                         Statistics.added_date, Statistics.telegram_id)
                                    ), 200)
    

def get_statistics(column_name:Column) ->list:
    result = db_session.query(
        column_name, func.count(column_name)
        ).group_by(column_name).all()
    return result
 

def get_statistics_by_days(column_name:Column, second_column_name:Column=None) -> dict:
    today = datetime.now().date()
    date_begin = today - timedelta(days=30)
    column_to_count = column_name if second_column_name is None else distinct(second_column_name)
    result = dict(
        db_session.query(
            func.to_char(column_name, 'YYYY-MM-DD'),
            func.count(column_to_count)
            ).filter(column_name > date_begin
            ).group_by(func.to_char(column_name, 'YYYY-MM-DD')
        ).all())
    return {
        (date_begin + timedelta(days=n)).strftime('%Y-%m-%d'):
            result.get((date_begin + timedelta(days=n)).strftime(
                '%Y-%m-%d'
            ), 0) for n in range(1, 31)
    }


def get_monthly_statistics(column_name:Column, second_column_name:Column):
    date_begin = datetime.now().date() - timedelta(days=30)
    result = db_session.query(
        func.count(distinct(second_column_name))
        ).filter(column_name > date_begin).all()
    return result[0][0]
