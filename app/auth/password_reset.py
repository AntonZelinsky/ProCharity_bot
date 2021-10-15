from smtplib import SMTPException

from sqlalchemy.exc import SQLAlchemyError

from app import config
from app.database import db_session
from app.models import AdminUser
from app.auth.send_token import send_token
from flask import jsonify, make_response
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_restful import Resource
from marshmallow import fields
from app.logger import app_logger as logger


class PasswordReset(MethodResource, Resource):
    """
    Provides password reset for admin users accounts.
    The password reset link is sent to the registered email address.
    """

    @doc(description="Reset user's password",
         tags=['Password Reset'],
         params={
             'email': {
                 'description': 'The registered user\' email address. The password reset link will be sent to the email.',
                 'in': 'query',
                 'type': 'string',
                 'required': True
             }
         }
         )
    @use_kwargs({'email': fields.Email()})
    def post(self, **kwargs):
        email = kwargs.get('email')
        user = AdminUser.query.filter_by(email=email).first()

        if not user:
            logger.info(f"Password reset: The specified user '{email}' does not exist.")
            return make_response(jsonify(message="Указанный пользователь не существует."), 400)

        subject = config.PASSWORD_RESET_SUBJECT
        template = config.PASSWORD_RESET_TEMPLATE
        path = 'password_reset_confirm'
        try:
            send_token(email, path, subject, template)
            db_session.commit()
        except SQLAlchemyError as ex:
            logger.error(f'Password reset: Database commit error "{str(ex)}"')
            db_session.rollback()
            return make_response(jsonify(message=f"Bad request: {str(ex)}"), 400)

        except SMTPException as ex:
            logger.error(f"Password reset:{str(ex)}")
            return make_response(jsonify(message=f"The message cannot be sent."), 400)

        logger.info(
            f"Password reset: The password reset link for the user {email} has been sent to the specified email.")
        return make_response(jsonify(message="Ссылка для сброса пароля была отправлена на указанную почту."), 200)
