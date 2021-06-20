from flask import jsonify
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from app.models import User, UserAdmin
from app import config
from app.apis.users import UserOperation

from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs

from marshmallow import fields


class Login(MethodResource, Resource, UserOperation):
    """
    Authorization of existing users by username and password.
    After authorization, the auth user receives a JWT token.
    This access token should be passed to the header.
    """

    @doc(description='This endpoint provides jwt token for authorized users',
         tags=['User Login'], )
    @use_kwargs({'email': fields.Str(), 'password': fields.Str()})
    def post(self, **kwargs):

        if not kwargs:
            return jsonify(message="This request requires 'email' and 'password'")

        email = kwargs.get("email")
        password = kwargs.get("password")

        if not email:
            return jsonify(message="email is required")

        if not password:
            return jsonify(message="Password is required")

        user = UserAdmin.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return jsonify(message="Bad email or Password")

        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)

        self.update_last_logon(user_obj=UserAdmin, id=user.id)

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
