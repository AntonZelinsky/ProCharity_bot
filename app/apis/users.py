from flask import jsonify
from flask_jwt_extended import jwt_required
from app import password_policy
from app.models import User
from app import config
from app.database import db_session
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs
from email_validator import validate_email, EmailNotValidError
from marshmallow import fields
import datetime

USER_SCHEMA = {
    'username': fields.Str(),
    "email": fields.Email(),
    'first_name': fields.Str(),
    'last_name': fields.Str(),
    'telegram_id': fields.Int(),
}


class UserOperation:
    """The class provides an interface for working with requests to user model.  """

    def exist_user(self, user_obj, username, email):
        check_email, check_username = (user_obj.query.filter_by(email=email).first(),
                                       user_obj.query.filter_by(username=username).first())

        if check_email or check_username:
            return True

    def exist_username(self, user_obj, username):
        if user_obj.query.filter_by(username=username).first():
            return True

    def exist_email(self, user_obj, email):
        if user_obj.query.filter_by(email=email).first():
            return True

    def check_input_credentials(self, password, email):
        if all((password, email)):
            return True

    def create_user(self, user_obj, **kwargs):
        user = user_obj(**kwargs)
        db_session.add(user)
        db_session.commit()

    def update_user(self, user_obj, id, **kwargs):
        user_obj.query.filter_by(id=id).update(kwargs)
        db_session.commit()

    def delete_user(self, user_obj, id):
        user = user_obj.query.get(id)
        db_session.delete(user)
        db_session.commit()

    def update_last_logon(self, user_obj, id):
        user = user_obj.query.get(id)
        user.last_logon = datetime.datetime.now()
        db_session.commit()

    def validate_password(self, password):
        if password_policy.validate(password):
            return True


class UsersList(MethodResource, Resource, UserOperation):
    """Provides access to 'get', 'post' requests for User model"""

    @doc(description='List of all users',
         tags=['Users Control'],
         params=config.PARAM_HEADER_AUTH
         )
    @jwt_required()
    def get(self):
        users = User.query.all()
        result = []

        for user in users:
            result.append(user.get_user_information())

        return jsonify(result)

    @doc(description="Add a new user's record in the database",
         tags=['Users Control'],
         params=config.PARAM_HEADER_AUTH
         )
    @jwt_required()
    @use_kwargs(USER_SCHEMA)
    def post(self, **kwargs):
        if not kwargs:
            return jsonify(message="The user's data not entered.")

        email = kwargs.get('email')
        username = kwargs.get('username')

        if self.exist_username(user_obj=User, username=username):
            return jsonify(message="The username already Exist")

        if self.exist_email(user_obj=User, email=email):
            return jsonify(message="The email already Exist")

        # email validation
        try:
            validate_email(email)

        except EmailNotValidError as ex:
            return jsonify(message=str(ex))

        self.create_user(user_obj=User, **kwargs)

        return jsonify(message='User has been created successfully')


class User_item(MethodResource, Resource, UserOperation):
    """Provides access to 'get', 'put' and 'delete' requests for items in User model"""

    @doc(description="Get one user's record",
         tags=['Users Control'],
         params=config.PARAM_HEADER_AUTH
         )
    @jwt_required()
    def get(self, id):
        user = User.query.get(id)
        if not user:
            return jsonify(message='This user was not found.')
        return jsonify(user.get_user_information())

    @doc(description="Update user's database information.",
         tags=['Users Control'],
         params=config.PARAM_HEADER_AUTH
         )
    @jwt_required()
    @use_kwargs(USER_SCHEMA)
    def put(self, id, **kwargs):
        username = kwargs.get('username')
        email = kwargs.get('email')

        if self.exist_username(user_obj=User, username=username):
            return jsonify(message='The user already exist.')

        if self.exist_email(user_obj=User, email=email):
            return jsonify(message='The email already exist.')

        # validate of an email if one included in the request.
        if email:
            try:
                validate_email(email)

            except EmailNotValidError as ex:
                return jsonify(message=str(ex))

        # validate of a password if one included in the request.

        # update request to DB
        self.update_user(user_obj=User, id=id, **kwargs)
        return jsonify(message='The user has been updated')

    @doc(description="Delete user record.",
         tags=['Users Control'],
         params=config.PARAM_HEADER_AUTH
         )
    @jwt_required()
    def delete(self, id):
        self.delete_user(id)
        return jsonify(message=f'The user ID:{id} has been deleted.')
