from flask import jsonify
from app.models import UserAdmin, Register
from app.apis.users import UserOperation
from werkzeug.security import generate_password_hash
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs
from email_validator import validate_email, EmailNotValidError
from marshmallow import fields
from datetime import timedelta, datetime
from app import config

USER_ADMIN_SCHEMA = {
    'email': fields.Str(),
    'first_name': fields.Str(),
    'last_name': fields.Str(),
    'password': fields.Str(),
    'last_logon': fields.Str(),
}


# TODO Complete!!!
class InvitationChecker(MethodResource, Resource):
    @use_kwargs(USER_ADMIN_SCHEMA)
    def post(self, **kwargs):
        token = kwargs.get('inv_t')
        record = Register.query.filter_by(token=token).first()
        if record:
            pass
            return jsonify(record)


class UserRegister(MethodResource, Resource, UserOperation):
    """Provides api for register new users"""

    @doc(description='This endpoint provide registering option for users.', tags=['User Registration'])
    @use_kwargs(USER_ADMIN_SCHEMA)
    def post(self, **kwargs):
        password = kwargs.get("password")
        email = kwargs.get("email")

        if not self.check_input_credentials(email=email,
                                            password=password):
            return jsonify("Registration request requires 'email' and 'password'.")

        if self.exist_email(user_obj=UserAdmin, email=email):
            return jsonify(message="The user or the email already Exist")

        # email validation
        try:
            validate_email(email)

        except EmailNotValidError as ex:
            return jsonify(message=str(ex))

        if not self.validate_password(password=password):
            return jsonify(message="The password does not comply with the password policy.")

        self.create_user(user_obj=UserAdmin, email=email,
                         password=generate_password_hash(password))

        return jsonify(message="User added successfully")
