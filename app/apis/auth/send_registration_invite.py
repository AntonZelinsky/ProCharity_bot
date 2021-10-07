from smtplib import SMTPException

from sqlalchemy.exc import SQLAlchemyError

from app import config
from app.database import db_session
from app.models import AdminUser
from email_validator import EmailNotValidError, validate_email
from flask import jsonify, make_response
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from marshmallow import fields
from app.logger import app_logger as logger
from app.apis.auth.send_token import send_token


class SendRegistrationInvite(MethodResource, Resource):
    @doc(description='Send email with invitation url',
         tags=['User Registration'],
         responses={200: {'description': 'Письмо с приглашением было отправлено на указанный адрес.'},
                    400: {'description': 'Пользователь с указанным почтовым адресом уже зарегистрирован.'},
                    500: {'description': "Server Error.."},

                    },
         params={
             'email': {
                 'description': 'The address to send the link to the registration invitation.',
                 'in': 'query',
                 'type': 'string',
                 'required': True
             },
             'Authorization': config.PARAM_HEADER_AUTH,
         }
         )
    @use_kwargs({'email': fields.Str()})
    @jwt_required()
    def post(self, **kwargs):
        email = kwargs.get('email').lower()

        if email:
            try:
                validate_email(email, check_deliverability=False)
            except EmailNotValidError as ex:
                logger.error(f"Send registration invite: {str(ex)}")
                return make_response(jsonify(message=str(ex)), 400)

        admin_user = AdminUser.query.filter_by(email=email).first()
        if admin_user:
            logger.info("Send registration invite:"
                        f" The user with the specified mailing address {email} is already registered.")
            return make_response(jsonify(
                message="Пользователь с указанным почтовым адресом уже зарегистрирован."), 400)
        subject = config.REGISTRATION_SUBJECT
        template = config.INVITATION_TEMPLATE
        path = 'register'
        try:
            send_token(email, path, subject, template)
            db_session.commit()
        except SQLAlchemyError as ex:
            logger.error(f'Send registration invite: Database commit error "{str(ex)}"')
            db_session.rollback()
            return make_response(jsonify(message=f'Bad request: {str(ex)}'), 400)

        except SMTPException as ex:
            logger.error(f"Send registration invite: {str(ex)}")
            return make_response(jsonify(message=f"The invitation message cannot be sent."), 400)

        logger.info(f"Send registration invite: "
                    f"The mail of invitation was sent to the specified address: {email}.")
        return make_response(jsonify(message="Письмо с приглашением было отправлено на указанный адрес."), 200)
