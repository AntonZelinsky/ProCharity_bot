import random
import string
from smtplib import SMTPException

from sqlalchemy.exc import SQLAlchemyError

from app import config
from app.database import db_session
from app.messages import send_email
from app.models import AdminUser
from flask import jsonify, make_response, render_template
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_restful import Resource
from marshmallow import fields
from werkzeug.security import generate_password_hash
from app.logger import app_logger as logger


class PasswordReset(MethodResource, Resource):
    """
    Provides password reset for admin users accounts
    The new password is sent to the registered email address.
    """

    @doc(description="Reset user's password",
         tags=['Password Reset'],
         params={
             'email': {
                 'description': 'The registered user\' email address.The password will be sent to the email.',
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
            logger.info(f"The specified user {email} does not exist.")
            return make_response(jsonify(message="Указанный пользователь не существует."), 400)
        password = self.random_password()

        subject = config.PASSWORD_RESET_SUBJECT
        template = render_template(config.PASSWORD_RESET_TEMPLATE, password=password)

        user.password = generate_password_hash(password=password)
        try:
            db_session.commit()
            send_email(subject=subject, template=template, recipients=[user.email])

        except SQLAlchemyError as ex:
            logger.exception(str(ex))
            db_session.rollback()
            return make_response(jsonify(message=f'Bad request: {str(ex)}'), 400)

        except SMTPException as ex:
            logger.error(str(ex))
            return make_response(jsonify(message=f'The invitation message cannot be sent.'), 400)

        logger.info(f"A new password for the user {email} has been sent to the specified email.")
        return make_response(jsonify(message="Новый пароль был выслан на указанную почту."), 200)

    def random_password(self):
        length = config.PASSWORD_POLICY["min_length"]
        chars = string.ascii_letters + string.digits + '!@#$%^&*()'
        rnd = random.SystemRandom()
        return ''.join(rnd.choice(chars) for i in range(length))
