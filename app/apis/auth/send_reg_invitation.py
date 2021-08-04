import uuid
from datetime import datetime, timedelta
from smtplib import SMTPException

from sqlalchemy.exc import SQLAlchemyError

from app import config
from app.database import db_session
from app.messages import send_email
from app.models import AdminRegistrationRequest, AdminUser
from email_validator import validate_email, EmailNotValidError
from flask import jsonify, make_response, render_template, request
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from marshmallow import fields
from app.logger import app_logger as logger


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
             # TODO Authorization is temporarily disabled.
             # 'Authorization': config.PARAM_HEADER_AUTH,  # Only if request requires authorization
         },

         )
    # TODO Token verification is temporarily disabled.
    @use_kwargs({'email': fields.Str()})
    # @jwt_required()
    def post(self, **kwargs):
        email = kwargs.get('email').lower()

        if email:
            try:
                validate_email(email, check_deliverability=False)
            except EmailNotValidError as ex:
                logger.exception(str(ex))
                return make_response(jsonify(message=str(ex)), 400)

        token_expiration = config.INV_TOKEN_EXPIRATION
        invitation_token_expiration_date = datetime.now() + timedelta(hours=token_expiration)
        invitation_token = str(uuid.uuid4())

        register_record = AdminRegistrationRequest.query.filter_by(email=email).first()

        if register_record:
            register_record.token = invitation_token
            register_record.token_expiration_date = invitation_token_expiration_date
            db_session.commit()
        else:

            admin_user = AdminUser.query.filter_by(email=email).first()
            if admin_user:
                logger.info(f"The user {email} with the specified email address is already registered")
                return make_response(jsonify(
                    message="Пользователь с указанным почтовым адресом уже зарегистрирован."), 400)

            user = AdminRegistrationRequest(
                email=email,
                token=invitation_token,
                token_expiration_date=invitation_token_expiration_date
            )

            db_session.add(user)

            try:
                db_session.commit()
            except SQLAlchemyError as ex:
                logger.exception(str(ex))
                db_session.rollback()
                return make_response(jsonify(message=f'Bad request: {str(ex)}'), 400)

        invitation_link = f'{request.scheme}://{config.HOST_NAME}/#/register/{invitation_token}'

        email_template = render_template(
            config.INVITATION_TEMPLATE,
            inv_link=invitation_link,
            expiration=token_expiration
        )
        try:
            send_email(
                recipients=[email],
                subject=config.REGISTRATION_SUBJECT,
                template=email_template
            )
        except SMTPException as ex:
            logger.error(str(ex))
            return make_response(jsonify(message=f'The invitation message cannot be sent.'), 400)

        logger.info(f"The mail of invitation was sent to the specified address: {email}.")
        return make_response(jsonify(message="Письмо с приглашением было отправлено на указанный адрес."), 200)
