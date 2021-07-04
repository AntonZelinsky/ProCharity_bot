import uuid
from datetime import datetime, timedelta

from app import config
from app.database import db_session
from app.messages import send_email
from app.models import Register, UserAdmin
from email_validator import EmailNotValidError, validate_email
from flask import jsonify, make_response, render_template
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from marshmallow import fields


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
        email = kwargs.get('email')

        # validate of an email if one included in the request.
        if email:
            try:
                validate_email(email, check_deliverability=False)

            except EmailNotValidError as ex:
                return make_response(jsonify(message=str(ex)), 400)

        subject = config.REGISTRATION_SUBJECT
        expiration = config.INV_TOKEN_EXPIRATION
        token_expiration_date = datetime.now() + timedelta(hours=config.INV_TOKEN_EXPIRATION)
        token = str(uuid.uuid4())
        inv_link = f'http://{config.HOST_NAME}/#/register/{token}'

        template = render_template(config.INVITATION_TEMPLATE, inv_link=inv_link, expiration=expiration)

        register_record = Register.query.filter_by(email=email).first()
        # checks if the invitation already sent.
        if register_record:
            # if the invitation request was sent before, update the token and exp. date
            register_record.token = token
            register_record.token_expiration_date = token_expiration_date
            db_session.commit()
        else:
            # if the invitation exist, try search the user in User Admin db
            admin_user = UserAdmin.query.filter_by(email=email).first()
            if admin_user:
                return make_response(jsonify(
                    message="Пользователь с указанным почтовым адресом уже зарегистрирован."), 400)

            user = Register(email=email, token=token, token_expiration_date=token_expiration_date)
            db_session.add(user)
            db_session.commit()

        try:
            send_email(recipients=[email], subject=subject, template=template)
        except Exception as ex:
            return make_response(jsonify(str(ex)), 500)

        return make_response(jsonify(message="Письмо с приглашением было отправлено на указанный адрес."), 200)
