from datetime import datetime

from app import password_policy
from app.database import db_session
from app.models import Register, UserAdmin
from flask import jsonify, make_response
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_restful import Resource
from marshmallow import fields, Schema
from werkzeug.security import generate_password_hash


class AdminUserRegistrationSchema(Schema):
    token = fields.String(required=True)
    first_name = fields.String(required=False)
    last_name = fields.String(required=False)
    password = fields.String(required=True)


class UserRegister(MethodResource, Resource):
    """Provides api for register a new Admin Users"""

    @doc(description='This endpoint provide registering option for admin users.', tags=['User Registration'],
         params={
             'token': {
                 'description': 'Invitation token',
                 'in': 'query',
                 'type': 'string',
                 'required': True
             },
             'first_name': {
                 'description': 'User\' First Name.',
                 'in': 'query',
                 'type': 'string',
                 'required': False
             },
             'last_name': {
                 'description': 'User\' Last Name.',
                 'in': 'query',
                 'type': 'string',
                 'required': False
             },
             'password': {
                 'description': 'Account password.',
                 'in': 'query',
                 'type': 'string',
                 'required': True
             },
         },
         responses={200: {'description': 'User registered successfully'},
                    400: {'description': "The password does not comply with the password policy."},
                    401: {'description': "The registration request requires a password."},
                    403: {'description': 'No invitation found or expired.'
                                         ' Please contact your site administrator.'},

                    }
         )
    @use_kwargs(AdminUserRegistrationSchema)
    def post(self, **kwargs):
        token = kwargs.get("token")
        password = kwargs.get("password")
        registration_record = Register.query.filter_by(token=token).first()

        if (not registration_record
                or registration_record.token_expiration_date < datetime.now()):
            return make_response(jsonify(message='No invitation found or expired.'
                                                 ' Please contact your site administrator.'), 403)
        # This key is no longer required.
        del kwargs['token']

        if not password:
            return make_response(jsonify("The registration request requires a password."), 401)

        kwargs['email'] = registration_record.email
        kwargs['password'] = generate_password_hash(password)

        if not password_policy.validate(password):
            return make_response(jsonify(message="The password does not comply with the password policy."), 400)

        # Create a new Admin user
        db_session.add(UserAdmin(**kwargs))
        # delete invitation
        db_session.delete(registration_record)
        db_session.commit()

        return make_response(jsonify(message="User registered successfully "), 200)
