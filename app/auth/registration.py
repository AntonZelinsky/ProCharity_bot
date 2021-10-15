from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from app import password_policy
from app.database import db_session
from app.models import AdminTokenRequest, AdminUser
from flask import jsonify, make_response
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_restful import Resource
from marshmallow import fields, Schema
from werkzeug.security import generate_password_hash
from app.logger import app_logger as logger


class AdminUserRegistrationSchema(Schema):
    token = fields.String(required=True)
    first_name = fields.String(required=False)
    last_name = fields.String(required=False)
    password = fields.String(required=True)


class UserRegister(MethodResource, Resource):
    """Provides api for register a new Admin Users"""

    @doc(description='This endpoint provide registering option for admin users.', tags=['User Registration'],
         params={
             'token': {
                 'description': 'Invitation token',
                 'in': 'query',
                 'type': 'string',
                 'required': True
             },
             'first_name': {
                 'description': 'User\' First Name.',
                 'in': 'query',
                 'type': 'string',
                 'required': False
             },
             'last_name': {
                 'description': 'User\' Last Name.',
                 'in': 'query',
                 'type': 'string',
                 'required': False
             },
             'password': {
                 'description': 'Account password.',
                 'in': 'query',
                 'type': 'string',
                 'required': True
             },
         },
         responses={200: {'description': 'Пользователь успешно зарегистрирован.'},
                    400: {'description': "Введенный пароль не соответствует политике паролей."},
                    401: {'description': "Для регистрации необходимо указать пароль."},
                    403: {'description': "Приглашение не было найдено или просрочено. "
                                         "Пожалуйста свяжитесь с своим системным администратором."},

                    }
         )
    @use_kwargs(AdminUserRegistrationSchema)
    def post(self, **kwargs):
        token = kwargs.get("token")
        password = kwargs.get("password")
        registration_record = AdminTokenRequest.query.filter_by(token=token).first()

        if (not registration_record
                or registration_record.token_expiration_date < datetime.now()):
            logger.info(f'Registration: The invitation "{token}" not found or expired.')
            return make_response(jsonify(message="Приглашение не было найдено или просрочено. "
                                                 "Пожалуйста свяжитесь с своим системным администратором."), 403)
        del kwargs['token']
        email = registration_record.email
        admin_user = AdminUser.query.filter_by(email=email).first()

        if admin_user:
            logger.info("Registration:"
                        f" The user with the specified mailing address {email} is already registered.")
            return make_response(jsonify(
                message="Пользователь с указанным почтовым адресом уже зарегистрирован."), 400)

        if not password:
            logger.info(f'Registration: The password for registration not passed. User: {email}')
            return make_response(jsonify("Для регистрации необходимо указать пароль."), 401)

        kwargs['email'] = email
        kwargs['password'] = generate_password_hash(password)

        if not password_policy.validate(password):
            logger.info(f'Registration: The entered password does not comply with the password policy. User: {email}.')
            return make_response(jsonify(message="Введенный пароль не соответствует политике паролей."), 400)

        db_session.add(AdminUser(**kwargs))
        db_session.delete(registration_record)
        try:
            db_session.commit()
        except SQLAlchemyError as ex:
            logger.error(f'Registration: Database commit error "{str(ex)}"')
            db_session.rollback()
            return make_response(jsonify(message=f'Bad request: {str(ex)}'), 400)

        logger.info(f'Registration: User {email} is successfully registered.')
        return make_response(jsonify(message="Пользователь успешно зарегистрирован."), 200)
