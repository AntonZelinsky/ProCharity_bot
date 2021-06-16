from flask import request, jsonify
from app.models import User
from app.database import db_session
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from werkzeug.security import generate_password_hash
from flask_restful import Resource
from email_validator import validate_email, EmailNotValidError


class Register(Resource):
    """This endpoint provide registering option for users.
        Requires:
            username: str
            password: str
            email: str
    """

    def post(self):
        if not request.get_json():
            return jsonify(message="Registration data is required")

        username = request.get_json()["username"]
        password = request.get_json()["password"]
        email = request.get_json()["email"]

        try:
            validate_email(email)

        except EmailNotValidError as ex:
            return jsonify(message=str(ex))

        check_email, check_username = (User.query.filter_by(email=email).first(),
                                       User.query.filter_by(username=username).first())

        if check_email or check_username:
            return jsonify(message="User Already Exist")

        user = User(username=username,
                    email=email,
                    password_hash=generate_password_hash(password),
                    is_superuser=False
                    )

        db_session.add(user)
        db_session.commit()
        return jsonify(message="User added successfully")


class Login(Resource):
    """This endpoint provides jwt token for authorized users.
        Required:
            username: str
            password: str
    """

    def post(self):
        username = request.get_json()["username"]
        password = request.get_json()["password"]

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return jsonify(message="Bad username or Password")

        access_token = create_access_token(identity=username)
        refresh_token = create_refresh_token(identity=username)

        return jsonify(access_token=access_token,
                       refresh_token=refresh_token)


class Refresh(Resource):
    """JWT token Refresh"""

    @jwt_required(refresh=True)
    def post(self):
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity, fresh=False)
        refresh_token = create_refresh_token(identity=identity)
        return jsonify(access_token=access_token, refresh_token=refresh_token)


class Users(Resource):
    """Users api"""

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
