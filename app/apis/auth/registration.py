from datetime import datetime

from app import password_policy
from app.database import db_session
from app.models import Register, UserAdmin
from flask import jsonify, make_response
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_restful import Resource
from marshmallow import fields
from werkzeug.security import generate_password_hash

USER_ADMIN_REGISTRATION_SCHEMA = {
    'token': fields.Str(),
    'first_name': fields.Str(),
    'last_name': fields.Str(),
    'password': fields.Str(),

}


class UserRegister(MethodResource, Resource):
    """Provides api for register a new Admin Users"""

    @doc(description='This endpoint provide registering option for admin users.', tags=['User Registration'])
    @use_kwargs(USER_ADMIN_REGISTRATION_SCHEMA)
    def post(self, **kwargs):
        token = kwargs.get("token")
        password = kwargs.get("password")
        registration_record = Register.query.filter_by(token=token).first()

        if not registration_record:
            return make_response(jsonify(message='No invitation found. Please contact your site administrator.'), 400)

        if registration_record.token_expiration_date < datetime.now():
            return make_response(jsonify(message='The invitation token has expired.'), 400)
        # This key is no longer required.
        del kwargs['token']

        if not password:
            return make_response(jsonify("The registration request requires a password."), 400)

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
