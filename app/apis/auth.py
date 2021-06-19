from flask import jsonify
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from app.models import User
from app import config
from app.apis.users import UserOperation
from werkzeug.security import generate_password_hash
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs
from email_validator import validate_email, EmailNotValidError
from marshmallow import fields


class Register(MethodResource, Resource, UserOperation):
    """Provides api for register new users"""

    @doc(description='This endpoint provide registering option for users.', tags=['User Registration'])
    @use_kwargs({'username': fields.Str(), 'password': fields.Str(), 'email': fields.Email()})
    def post(self, **kwargs):
        username = kwargs.get("username")
        password = kwargs.get("password")
        email = kwargs.get("email")

        if not self.check_input_credentials(username=username,
                                            email=email,
                                            password=password):
            return jsonify("Registration request requires 'username', 'password' and 'email address'.")

        # email validation
        try:
            validate_email(email)

        except EmailNotValidError as ex:
            return jsonify(message=str(ex))

        if self.exist_user(username=username, email=email):
            return jsonify(message="The user or the email already Exist")

        if not self.validate_password(password=password):
            return jsonify(message="The password does not comply with the password policy.")

        self.create_user(username=username,
                         email=email,
                         password=generate_password_hash(password),
                         is_superuser=False)

        return jsonify(message="User added successfully")


class Login(MethodResource, Resource, UserOperation):
    """
    Authorization of existing users by username and password.
    After authorization, the auth user receives a JWT token.
    This access token should be passed to the header.
    """

    @doc(description='This endpoint provides jwt token for authorized users',
         tags=['User Login'], )
    @use_kwargs({'username': fields.Str(), 'password': fields.Str()})
    def post(self, **kwargs):

        if not kwargs:
            return jsonify(message="This request requires 'username' and 'password'")

        username = kwargs.get("username")
        password = kwargs.get("password")

        if not username:
            return jsonify(message="Username is required")

        if not password:
            return jsonify(message="Password is required")

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return jsonify(message="Bad username or Password")

        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)

        self.update_last_logon(id=user.id)

        return jsonify(access_token=access_token,
                       refresh_token=refresh_token)


class Refresh(MethodResource, Resource):
    """The endpoint provides access to refresh a JWT token"""

    @doc(description='JWT token Refresh API',
         tags=['JWT Refresh'],
         params=config.PARAM_HEADER_AUTH
         )
    @jwt_required(refresh=True)
    def post(self):
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity, fresh=False)
        refresh_token = create_refresh_token(identity=identity)
        return jsonify(access_token=access_token, refresh_token=refresh_token)


# TODO Complete password reset
class PasswordReset(MethodResource, Resource, UserOperation):
    """Provides password reset for users accounts"""

    # TODO Send a new password to user's email
    # TODO Send a new password to telegramm chat.
    @doc(description="Reset user's password",
         tags=['Password Reset'],
         params=config.PARAM_HEADER_AUTH
         )
    @use_kwargs({'message': fields.Str()})
    @jwt_required()
    def post(self, username=None, email=None):
        pass
