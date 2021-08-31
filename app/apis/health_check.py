from flask import jsonify, make_response
from flask_apispec import doc
from flask_apispec.views import MethodResource
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func

from app.models import User, Task
from app.database import db_session
from app.logger import app_logger as logger

from bot import charity_bot


class HealthCheck(MethodResource, Resource):
    @doc(description='HealthСheck checks the connection to the database and bot',
         tags=['HealthCheck'])

    def get(self):
        return make_response(jsonify(db=check_db_connection(),
                                     bot=check_bot()), 200)


def check_db_connection():
        try:
            db_session.query(User).first()
            logger.info(f'Health check: database connection succeeded')
            return dict(db_connection=True,
                        last_update=get_last_update(),
                        active_tasks = get_count_active_tasks())
        except SQLAlchemyError as ex:
            logger.error(f'Health check: Database error "{str(ex)}"')
            return dict(db_connection=False,
                        db_connection_error=f'{ex}')

def get_last_update():
    result = db_session.query(
                func.to_char(Task.updated_date, 'YYYY-MM-DD HH24:MI:SS')
                ).order_by(Task.updated_date.desc()).first()
    return result[0]


def get_count_active_tasks():
    result = len(db_session.query(Task.archive).filter(Task.archive == False).all())
    return result


def check_bot():
    try:
        result = charity_bot.updater.bot.get_webhook_info()
        return dict(bot_connection=True, method='pulling', info=f'{result}')
    except Exception as ex:
        return dict(bot_connection=False, error=f'{ex}')
