from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask import jsonify, render_template, make_response
from flask_apispec import doc, use_kwargs
from flask_jwt_extended import jwt_required
from app import config
from marshmallow import fields
from app.messages import send_email
import uuid
from app.models import Register, UserAdmin
from datetime import datetime, timedelta
from app.database import db_session
from email_validator import validate_email, EmailNotValidError


class SendRegistrationInvitation(MethodResource, Resource):
    @doc(description='Send email with invitation url',
         tags=['User Registration'],
         params=config.PARAM_HEADER_AUTH
         )
    @use_kwargs({'email': fields.Str()})
    @jwt_required()
    def post(self, **kwargs):
        email = kwargs.get('email')

        # validate of an email if one included in the request.
        if email:
            try:
                validate_email(email)

            except EmailNotValidError as ex:
                return make_response(jsonify(message=str(ex)), 400)

        subject = config.SUBJECT
        expiration = config.INV_TOKEN_EXPIRATION
        token_expiration_date = datetime.now() + timedelta(hours=config.INV_TOKEN_EXPIRATION)
        token = str(uuid.uuid4())
        inv_link = f'{config.HOST_NAME}/register/?token:{token}'

        template = render_template(config.INVITATION_TEMPLATE, inv_link=inv_link, expiration=expiration)

        register_record = Register.query.filter_by(email=email).first()
        # checks if the invitation already sent.
        if register_record:
            # if the invitation exist, try search the user in User Admin db
            admin_user = UserAdmin.query.filter_by(email=email).first()
            if admin_user:
                return make_response(jsonify('The user already exist in the database.'), 400)

            register_record.token = token
            register_record.token_expiration_date = token_expiration_date
            db_session.commit()
        else:
            user = Register(email=email, token=token, token_expiration_date=token_expiration_date)
            db_session.add(user)
            db_session.commit()

        try:
            send_email(recipients=[email], subject=subject, template=template)
        except Exception as ex:
            return make_response(jsonify(str(ex)), 400)

        return jsonify('The email with the invitation url was been sent to specified email address')
