from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from app import password_policy
from app.database import db_session
from app.models import AdminTokenRequest, AdminUser
from flask import jsonify, make_response
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_restful import Resource
from marshmallow import fields
from werkzeug.security import generate_password_hash
from app.logger import app_logger as logger


class PasswordResetConfirm(MethodResource, Resource):

    @doc(description='This endpoint provides the ability to change the password for admins.',
         tags=['Password Reset'],
         params={
             'token': {
                 'description': 'Password reset token',
                 'in': 'query',
                 'type': 'string',
                 'required': True
             },
             'password': {
                 'description': 'Password.',
                 'in': 'query',
                 'type': 'string',
                 'required': True
             },
         },
         responses={200: {'description': 'Пароль успешно изменен.'},
                    400: {'description': 'Введенный пароль не соответствует политике паролей.'},
                    401: {'description': 'Необходимо указать пароль.'},
                    403: {'description': 'Токен не был найден или просрочен. '
                                         'Пожалуйста свяжитесь со своим системным администратором.'},

                    }
         )
    @use_kwargs({'token': fields.Str(), 'password': fields.Str()})
    def post(self, **kwargs):
        token = kwargs.get('token')
        password = kwargs.get('password')
        reset_record = AdminTokenRequest.query.filter_by(token=token).first()
        email = reset_record.email

        if (not reset_record
                or reset_record.token_expiration_date < datetime.now()):
            logger.info(f'Password reset confirm: Token "{token}" not found or expired.')
            return make_response(jsonify(message='Токен не был найден или просрочен. '
                                                 'Пожалуйста свяжитесь со своим системным администратором.'), 403)

        if not password:
            logger.info(f'Password reset confirm: The password for reset not passed. User: {email}')
            return make_response(jsonify("Необходимо указать пароль."), 401)

        if not password_policy.validate(password):
            logger.info(
                f'Password reset confirm: The entered password does not comply with the password policy. User: {email}.')
            return make_response(jsonify(message="Введенный пароль не соответствует политике паролей."), 400)

        user = AdminUser.query.filter_by(email=email).first()
        user.password = generate_password_hash(password)
        db_session.delete(reset_record)
        try:
            db_session.commit()
        except SQLAlchemyError as ex:
            logger.error(f'Registration: Database commit error "{str(ex)}"')
            db_session.rollback()
            return make_response(jsonify(message=f'Bad request: {str(ex)}'), 400)

        logger.info(f'Registration: User {email} is successfully registered.')
        return make_response(jsonify(message="Пароль успешно изменен."), 200)
