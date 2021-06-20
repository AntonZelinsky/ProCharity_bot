from flask import jsonify, make_response
from flask_jwt_extended import create_access_token, create_refresh_token
from app.models import UserAdmin
from app.database import db_session
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs
import datetime
from marshmallow import fields


class Login(MethodResource, Resource):
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
            return jsonify(message="This request requires 'email' and 'password'"), 400

        email = kwargs.get("email")
        password = kwargs.get("password")

        if not email:
            return make_response(jsonify(message="email is required"), 400)

        if not password:
            return make_response(jsonify(message="Password is required"), 400)

        user = UserAdmin.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return make_response(jsonify(message="Bad email or Password"), 400)

        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)

        # update last logon
        user = UserAdmin.query.get(user.id)
        user.last_logon = datetime.datetime.now()
        db_session.commit()

        return jsonify(access_token=access_token,
                       refresh_token=refresh_token)
