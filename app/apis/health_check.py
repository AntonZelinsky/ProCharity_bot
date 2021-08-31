from flask import jsonify, make_response
from flask_apispec import doc
from flask_apispec.views import MethodResource
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError

from app.models import User
from app.database import db_session
from app.logger import app_logger as logger


class Health(MethodResource, Resource):
    @doc(description='Health check',
         tags=['Health'])

    def get(self):
        try:
            db_session.query(User).first()
            logger.info(f'Health check: database connection succeeded')
            return make_response(jsonify(check_db_connection='OK'), 200)
        except SQLAlchemyError as ex:
            logger.error(f'Health check: Database error "{str(ex)}"')
