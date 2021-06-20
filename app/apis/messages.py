from flask_restful import Resource, request
from flask_apispec.views import MethodResource
from flask import jsonify, render_template
from flask_apispec import doc, use_kwargs
from flask_jwt_extended import jwt_required
from app import config
from marshmallow import fields
from app.messages import send_email
import uuid
from app.models import Register, UserAdmin
import datetime
from app.database import db_session
from email_validator import validate_email, EmailNotValidError


# TODO Complete push messages from admin panel
class SendMessage(MethodResource, Resource):
    @doc(description='Send message to registered users',
         tags=['Send Message'],
         params=config.PARAM_HEADER_AUTH
         )
    @use_kwargs({'message': fields.Str()})
    @jwt_required()
    def post(self):
        return jsonify(message='Message has been sent to users')


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
                return jsonify(message=str(ex))

        subject = config.SUBJECT
        now = datetime.datetime.now()
        token = str(uuid.uuid4())
        inv_link = f'{request.host_url}/register/?inv_token:{token}'

        template = render_template(config.INVITATION_TEMPLATE, inv_link=inv_link)

        register_record = Register.query.filter_by(email=email).first()
        # checks if the invitation already sent.
        if register_record:
            # if the invitation exist, try search the user in User Admin db
            admin_user = UserAdmin.query.filter_by(email=email).first()
            if admin_user:
                return jsonify('The user already exist in the database.')

            register_record.token = token
            register_record.inv_created_date = now
            db_session.commit()
        else:
            user = Register(email=email, token=token, inv_created_date=now)
            db_session.add(user)
            db_session.commit()

        try:
            send_email(recipients=[email], subject=subject, template=template)
        except Exception as ex:
            return jsonify(str(ex))

        return jsonify('The email with the invitation url was been sent to specified email address')
