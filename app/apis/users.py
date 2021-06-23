from flask import jsonify, make_response
from flask_jwt_extended import jwt_required
from app.models import User
from app import config
from app.database import db_session
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs
from email_validator import validate_email, EmailNotValidError
from marshmallow import fields

USER_SCHEMA = {
    'username': fields.Str(),
    "email": fields.Email(),
    'first_name': fields.Str(),
    'last_name': fields.Str(),
    'telegram_id': fields.Int(),
}


class UsersList(MethodResource, Resource):
    """Provides access to 'get', 'post' requests for User model"""

    @doc(description='List of all users',
         tags=['Users Control'],
         params={'Authorization': config.PARAM_HEADER_AUTH, })
    @jwt_required()
    def get(self):
        users = User.query.all()
        result = []

        for user in users:
            result.append(user.get_user_information())

        return make_response(jsonify(result), 200)


class User_item(MethodResource, Resource):
    """Provides access to 'get', 'put' and 'delete' requests for items in User model"""

    @doc(description="Get one user's record",
         tags=['Users Control'],
         params={'Authorization': config.PARAM_HEADER_AUTH, }
         )
    @jwt_required()
    def get(self, id):
        user = User.query.get(id)
        if not user:
            return make_response(jsonify(message='This user was not found.'), 400)
        return make_response(jsonify(user.get_user_information()), 200)

    @doc(description="Update user's database information.",
         tags=['Users Control'],
         params={
             'username': {
                 'description': 'The user\' telegram username.',
                 'in': 'query',
                 'type': 'string',
                 'required': False
             },
             'email': {
                 'description': 'User\'s email.',
                 'in': 'query',
                 'type': 'string',
                 'required': False

             },
             'first_name': {
                 'description': 'First Name',
                 'in': 'query',
                 'type': 'string',
                 'required': False
             },
             'last_name': {
                 'description': 'Last Name',
                 'in': 'query',
                 'type': 'string',
                 'required': False
             },
             'chat_id': {
                 'description': 'User\' chat_id.',
                 'in': 'query',
                 'type': 'integer',
                 'required': False,
             },
             'Authorization': config.PARAM_HEADER_AUTH,  # Only if request requires authorization
         }
         )
    @jwt_required()
    @use_kwargs(USER_SCHEMA)
    def put(self, id, **kwargs):
        username = kwargs.get('username')
        email = kwargs.get('email')

        if User.query.filter_by(username=username).first():
            return make_response(jsonify(message='The user already exist.'), 400)

        if User.query.filter_by(email=email).first():
            return make_response(jsonify(message='The email already exist.'), 400)

        # validate of an email if one included in the request.
        if email:
            try:
                validate_email(email)

            except EmailNotValidError as ex:
                return make_response(jsonify(message=str(ex)), 400)

            # validate of a password if one included in the request.

            # update request to DB
        User.query.filter_by(id=id).update(kwargs)
        db_session.commit()

        return make_response(jsonify(message='The user has been updated'), 200)

    @doc(description="Delete user record.",
         tags=['Users Control'],
         params={'Authorization': config.PARAM_HEADER_AUTH, }
         )
    @jwt_required()
    def delete(self, id):
        user = User.query.get(id)
        if not user:
            return make_response(jsonify(message=f'The user did not found.'), 400)
        db_session.delete(user)
        db_session.commit()
        return make_response(jsonify(message=f'The user ID:{id} has been deleted.'), 200)
