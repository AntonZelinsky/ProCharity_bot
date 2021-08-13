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
        reasons_canceling_from_db = get_statistics(ReasonCanceling.reason_canceling)
        reasons_canceling = {
            constants.REASONS.get(key, 'Другое'):
                value for key, value in reasons_canceling_from_db
        }
        return make_response(jsonify(added_users=get_statistics_by_days(User.date_registration),
                                     added_external_users=get_statistics_by_days(User.external_signup_date),
                                     number_users = get_number_users_statistic(),
                                     command_stats=dict(get_statistics(Statistics.command)),
                                     reasons_canceling=reasons_canceling,
                                     users_unsubscribed=get_statistics_by_days(ReasonCanceling.added_date),
                                     distinct_users_unsubscribed=get_statistics_by_days(
                                         ReasonCanceling.added_date, ReasonCanceling.telegram_id),
                                     active_users_statistic=users_activity_statistic(Statistics.added_date,
                                                                                     Statistics.telegram_id),
                                     ), 200)


TODAY = datetime.now().date()
DATE_BEGIN = TODAY - timedelta(days=30)


def get_number_users_statistic():
    users = db_session.query(User.has_mailing, User.banned).all()
    number_users = len(users)
    # user[0] - has_mailing, user[1] - banned
    subscribed_users = len([user for user in users if user[0] and not user[1]])
    not_subscribed_users = len([user for user in users if not user[0] and not user[1]])
    banned_users = len([user for user in users if user[1]])
    return {
        'all_users': number_users,
        'subscribed_users': subscribed_users,
        'not_subscribed_users': not_subscribed_users,
        'banned_users': banned_users,
    }


def get_statistics(column_name: Column) -> list:
    result = db_session.query(
        column_name, func.count(column_name)
    ).group_by(column_name).all()
    return result


def get_monthly_statistics(column_name: Column, second_column_name: Column):
    result = db_session.query(
        func.count(distinct(second_column_name))
    ).filter(column_name > DATE_BEGIN).all()
    return result[0][0]


def get_statistics_by_days(column_name: Column, second_column_name: Column = None) -> dict:
    column_to_count = column_name if second_column_name is None else distinct(second_column_name)
    result = dict(
        db_session.query(
            func.to_char(column_name, 'YYYY-MM-DD'),
            func.count(column_to_count))
            .filter(column_name > DATE_BEGIN)
            .group_by(func.to_char(column_name, 'YYYY-MM-DD'))
            .all())
    return get_dict_by_days(result)


def get_dict_by_days(result):
    return {
        (DATE_BEGIN + timedelta(days=n)).strftime('%Y-%m-%d'):
            result.get((DATE_BEGIN + timedelta(days=n))
            .strftime('%Y-%m-%d'), 0)
            for n in range(1, 31)
    }


def get_statistic_by_days_with_filtration(column_name: Column, second_column_name: Column, filter_list: list):
    column_to_count = distinct(second_column_name)
    result = dict(
        db_session.query(
            func.to_char(column_name, 'YYYY-MM-DD'),
            func.count(column_to_count))
            .filter(column_name > DATE_BEGIN)
            .filter(second_column_name.in_(filter_list))
            .group_by(func.to_char(column_name, 'YYYY-MM-DD'))
            .all())
    return get_dict_by_days(result)


def users_activity_statistic(column_name: Column, second_column_name: Column = None):
    users = db_session.query(User.telegram_id, User.has_mailing).all()
    subscribed_users_ids = [user[0] for user in users if user[1] is True]
    unsubscribed_users_ids = [user[0] for user in users if user[1] is False]

    all_active_users = get_statistics_by_days(column_name, second_column_name)
    subscribed_active_users = get_statistic_by_days_with_filtration(column_name, second_column_name,
                                                                    subscribed_users_ids)
    unsubscribed_active_users = get_statistic_by_days_with_filtration(column_name, second_column_name,
                                                                      unsubscribed_users_ids)
    active_users_per_month = get_monthly_statistics(column_name, second_column_name)
    result = {
        'all': all_active_users,
        'subscribed': subscribed_active_users,
        'unsubscribed': unsubscribed_active_users,
        'active_users_per_month': active_users_per_month
    }
    return result
