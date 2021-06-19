from flask import jsonify
from flask_jwt_extended import jwt_required
from app import password_policy
from app.models import User
from app import config
from app.database import db_session
from werkzeug.security import generate_password_hash
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs
from email_validator import validate_email, EmailNotValidError
from marshmallow import fields
import datetime


USER_SCHEMA = {
    'username': fields.Str(),
    'password': fields.Str(),
    "email": fields.Email(),
    'first_name': fields.Str(),
    'last_name': fields.Str(),
    'telegram_id': fields.Int(),
    'is_superuser': fields.Bool(),
    'mailing': fields.Bool(),
}


class UserOperation:
    """The class provides an interface for working with requests to user model.  """

    def exist_user(self, username, email):
        check_email, check_username = (User.query.filter_by(email=email).first(),
                                       User.query.filter_by(username=username).first())

        if check_email or check_username:
            return True

    def exist_username(self, username):
        if User.query.filter_by(username=username).first():
            return True

    def exist_email(self, email):
        if User.query.filter_by(email=email).first():
            return True

    def check_input_credentials(self, username, password, email):
        if all((username, password, email)):
            return True

    def create_user(self, **kwargs):
        user = User(**kwargs)
        db_session.add(user)
        db_session.commit()

    def update_user(self, id, **kwargs):
        User.query.filter_by(id=id).update(kwargs)
        db_session.commit()

    def delete_user(self, id):
        user = User.query.get(id)
        db_session.delete(user)
        db_session.commit()

    def update_last_logon(self, id):
        user = User.query.get(id)
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
        password = kwargs.get('password')

        if not self.check_input_credentials(username=username, email=email, password=password):
            return jsonify("Registration request requires 'username', 'password' and 'email address'.")

        if self.exist_user(username=username, email=email):
            return jsonify(message="The user or the email already Exist")

        # email validation
        try:
            validate_email(email)

        except EmailNotValidError as ex:
            return jsonify(message=str(ex))

        # Password check for password policy compliance
        if not self.validate_password(password=password):
            return jsonify(message="The password does not comply with the password policy.")

        # Create a new user
        kwargs['password'] = generate_password_hash(password)
        self.create_user(**kwargs)

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
        if user:
            return jsonify(user.get_user_information())

    @doc(description="Update user's database information.",
         tags=['Users Control'],
         params=config.PARAM_HEADER_AUTH
         )
    @jwt_required()
    @use_kwargs(USER_SCHEMA)
    def put(self, id, **kwargs):
        username = kwargs.get('username')
        password = kwargs.get('password')
        email = kwargs.get('email')

        if self.exist_username(username=username):
            return jsonify(message='The user already exist.')

        if self.exist_email(email=email):
            return jsonify(message='The email already exist.')

        # validate of an email if one included in the request.
        if email:
            try:
                validate_email(email)

            except EmailNotValidError as ex:
                return jsonify(message=str(ex))

        # validate of a password if one included in the request.
        if password:
            if not self.validate_password(password=password):
                return jsonify(message="The password does not comply with the password policy.")
            kwargs['password'] = generate_password_hash(password)

        # update request to DB

        self.update_user(id, **kwargs)
        return jsonify(message='The user has been updated')

    @doc(description="Delete user record.",
         tags=['Users Control'],
         params=config.PARAM_HEADER_AUTH
         )
    @jwt_required()
    def delete(self, id):
        self.delete_user(id)
        return jsonify(message=f'The user ID:{id} has been deleted.')
