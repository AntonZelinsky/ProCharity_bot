import datetime

from app.database import db_session
from app.models import UserAdmin
from flask import jsonify, make_response
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_restful import Resource
from marshmallow import fields, Schema


class LoginSchema(Schema):
    email = fields.String(required=True)
    password = fields.String(required=True)


class Login(MethodResource, Resource):
    """
    Authorization of existing users by username and password.
    After authorization, the auth user receives a JWT token.
    This access token should be passed to the header.
    """

    @doc(description='This endpoint provides jwt token for authorized users',
         tags=['User Login'],
         params={
             'email': {
                 'description': 'The registered user\' email address.',
                 'in': 'query',
                 'type': 'string',
                 'required': True
             },
             'password': {
                 'description': 'User\'s password.',
                 'in': 'query',
                 'type': 'string',
                 'required': True
             }
         },
         responses={200: {'description': 'access_token:"" refresh_token: ""'},
                    403: {'description': "'Email and password is required.', 'Bad email or Password.'"},

                    }
         )
    @use_kwargs(LoginSchema)
    def post(self, **kwargs):
        if not kwargs:
            return make_response(jsonify(message="Email and password is required"), 403)

        email = kwargs.get("email")
        password = kwargs.get("password")

        if not email or not password:
            return make_response(jsonify(message="Email and password is required"), 403)

        user = UserAdmin.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return make_response(jsonify(message="Bad email or Password"), 403)

        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)

        # update last logon
        user = UserAdmin.query.get(user.id)
        user.last_logon = datetime.datetime.now()
        db_session.commit()

        return make_response(jsonify(access_token=access_token,
                                     refresh_token=refresh_token), 200)
