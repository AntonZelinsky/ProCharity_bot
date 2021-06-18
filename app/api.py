from flask import jsonify
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from app import password_policy
from app.models import User
from app.database import db_session
from werkzeug.security import generate_password_hash
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs
from email_validator import validate_email, EmailNotValidError
from marshmallow import fields
import datetime


class UserOperation:
    """The class provides an interface for working with requests to users creation.  """

    PARAM_HEADER_AUTH = {
        'Authorization': {
            'description':
                'HTTP header with JWT access token, like: Authorization: Bearer asdf.qwer.zxcv',
            'in': 'header',
            'type': 'string',
            'required': True
        }
    }

    def __init__(self, username=None, password=None, email=None):
        self.username = username
        self.password = password
        self.email = email

    def exist_user(self, username, email):
        check_email, check_username = (User.query.filter_by(email=email).first(),
                                       User.query.filter_by(username=username).first())

        if check_email or check_username:
            return True

    def check_input_credentials(self, username, password, email):
        if all((username, password, email)):
            return True

    def create_user(self, **kwargs):
        user = User(**kwargs)
        db_session.add(user)
        db_session.commit()

    def update_user(self, username, **kwargs):
        User.query.filter_by(username=username).update(kwargs)
        db_session.commit()

    def delete_user(self, username):
        user = User.query.filter_by(username=username).first()
        db_session.delete(user)
        db_session.commit()

    def update_last_logon(self, username):
        user = User.query.filter_by(username=username).first()
        user.last_logon = datetime.datetime.now()
        db_session.commit()

    def validate_password(self, password):
        if password_policy.validate(password):
            return True


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

        self.update_last_logon(username=username)

        return jsonify(access_token=access_token,
                       refresh_token=refresh_token)


class Refresh(MethodResource, Resource):
    """The endpoint provides access to refresh a JWT token"""

    @doc(description='JWT token Refresh API',
         tags=['JWT Refresh'],
         params=UserOperation.PARAM_HEADER_AUTH
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
    def post(self, username=None, email=None):
        pass


# TODO Complete push messages from admin panel
class SendMessage(MethodResource, Resource):
    def post(self, message=None):
        pass


class UsersList(MethodResource, Resource, UserOperation):
    """Provides access to 'get', 'post' requests for User model"""

    @doc(description='List of all users',
         tags=['Users Control'],
         params=UserOperation.PARAM_HEADER_AUTH
         )
    @jwt_required()
    def get(self):
        users = User.query.all()
        result = []

        for u in users:
            users = {}
            users['username'] = u.username
            users['email'] = u.email
            users['is_superuser'] = u.is_superuser
            result.append(users)

        return jsonify(message=result)

    @doc(description="Add a new user's record in the database",
         tags=['Users Control'],
         params=UserOperation.PARAM_HEADER_AUTH
         )
    @jwt_required()
    @use_kwargs({
        'username': fields.Str(),
        'password': fields.Str(),
        "email": fields.Email(),
        'telegram_id': fields.Int(),
        'first_name': fields.Str(),
        'last_name': fields.Str(),
        'is_superuser': fields.Bool(),
        'mailing': fields.Bool(),
    }
    )
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

    @doc(description="Get one users record",
         tags=['Users Control'],
         params=UserOperation.PARAM_HEADER_AUTH
         )
    @jwt_required()
    def get(self, username):
        user = User.query.filter_by(username=username).first()
        if user:
            return jsonify(user.get_user_information())

    @doc(description="Update user's database information.",
         tags=['Users Control'],
         params=UserOperation.PARAM_HEADER_AUTH
         )
    @jwt_required()
    @use_kwargs({
        'password': fields.Str(),
        "email": fields.Email(),
        'telegram_id': fields.Int(),
        'first_name': fields.Str(),
        'last_name': fields.Str(),
        'is_superuser': fields.Bool(),
        'mailing': fields.Bool(),
    }
    )
    def put(self, username, **kwargs):
        password = kwargs.get('password')
        email = kwargs.get('email')

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
        self.update_user(username, **kwargs)
        return jsonify(message='The user has been updated')

    @doc(description="Delete user record.",
         tags=['Users Control'],
         params=UserOperation.PARAM_HEADER_AUTH
         )
    @jwt_required()
    def delete(self, username):
        self.delete_user(username=username)
        return jsonify(message=f'The user {username} has been deleted.')
