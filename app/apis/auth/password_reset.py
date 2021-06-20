from flask_jwt_extended import jwt_required
from app import config
from app.apis.users import UserOperation

from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs

from marshmallow import fields


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
