import os
import datetime
import git

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
                                     bot=check_bot(),
                                     git=get_last_commit()), 200)


def check_db_connection():
    try:
        db_session.query(User).first()
        logger.info(f'Health check: Database connection succeeded')
        return dict(status=True,
                    last_update=get_last_update(),
                    active_tasks=get_count_active_tasks())
    except SQLAlchemyError as ex:
        logger.critical(f'Health check: Database error "{str(ex)}"')
        return dict(status=False,
                    db_connection_error=f'{ex}')


def get_last_update():
    result = db_session.query(
        func.to_char(Task.updated_date, 'YYYY-MM-DD HH24:MI:SS')
    ).order_by(Task.updated_date.desc()).first()
    return result[0]


def get_count_active_tasks():
    result = db_session.query(func.count(Task.archive)).filter(Task.archive == False).all()
    return result[0][0]


def check_bot():
    try:
        charity_bot.updater.bot.get_webhook_info()
        logger.info(f'Health check: Bot connection succeeded')
        return dict(status=True, method='pulling')
    except Exception as ex:
        logger.critical(f'Health check: Bot error "{str(ex)}"')
        return dict(status=False, error=f'{ex}')


def get_last_commit():
    repo = git.Repo(os.getcwd())
    master = repo.head.reference
    commit_date = datetime.datetime.fromtimestamp(master.commit.committed_date)
    last_tag = repo.tags[-1]
    tag = str(last_tag) if master.commit == last_tag.commit else None
    result = dict(last_commit=str(master.commit)[:7],
                  commit_date=commit_date.strftime("%Y-%m-%d %H:%M:%S"),
                  tag=tag)
    return result
