from email_validator import validate_email, EmailNotValidError
from flask import jsonify, make_response, request
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from marshmallow import fields
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy_pagination import paginate

from app import config
from app import formatter
from app.database import db_session
from app.logger import app_logger as logger
from app.swagger_schemas import USERS_SCHEMA
from app.models import User
from . import front_api as api


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
         params={'page': {
             'description': 'Number of page',
             'in': 'query',
             'type': 'integer',
             'required': True
         },

             'limit': {
                 'description': 'Limit of items on one page',
                 'in': 'query',
                 'type': 'integer',
                 'default': 10,
                 'required': True
             },
             'Authorization': config.PARAM_HEADER_AUTH,

         },
         responses=USERS_SCHEMA

         )
    @jwt_required()
    def get(self):
        result = []
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', config.PAGE_LIMIT))
        paginate_page = paginate(db_session.query(User), page, limit)

        for item in paginate_page.items:
            result.append(formatter.user_formatter(item))

        next_url = None
        previous_url = None
        if paginate_page.has_next:
            next_url = f'{api.url_for(UsersList)}?page={page + 1}&limit={limit}'

        if paginate_page.has_previous:
            previous_url = f'{api.url_for(UsersList)}?page={page - 1}&limit={limit}'

        return make_response(jsonify(
            {
                'total': paginate_page.total,
                'pages': paginate_page.pages,
                'previous_page': paginate_page.previous_page,
                'current_page': page,
                'next_page': paginate_page.next_page,
                'next_url': next_url,
                'previous_url': previous_url,
                'result': result
            },
        ),
            200
        )


class UserItem(MethodResource, Resource):
    """Provides access to 'get', 'put' and 'delete' requests for items in User model"""

    @doc(description="Get one user's record",
         tags=['Users Control'],
         params={'Authorization': config.PARAM_HEADER_AUTH, }
         )
    @jwt_required()
    def get(self, telegram_id):
        user = User.query.get(telegram_id)
        if not user:
            logger.info(f'Users: The user{telegram_id} not found.')
            return make_response(jsonify(message='Данный пользователь не найден.'), 400)
        logger.info(f'Users: Requested users list was provided.')
        return make_response(jsonify(formatter.user_formatter(user)), 200)

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
    def put(self, telegram_id, **kwargs):
        username = kwargs.get('username')
        email = kwargs.get('email')

        if User.query.filter_by(username=username).first():
            logger.info(f'Users: The specified user {username} already exists')
            return make_response(jsonify(message='Указанный пользователь уже существует.'), 400)

        if User.query.filter_by(email=email).first():
            logger.info(f'Users: The specified email {email} already exists')
            return make_response(jsonify(message='Указанный почтовый адрес уже существует.'), 400)

        if email:
            try:
                validate_email(email, check_deliverability=False)
            except EmailNotValidError as ex:
                logger.error(f'Users: {str(ex)}')
                return make_response(jsonify(message=str(ex)), 400)

        User.query.filter_by(telegram_id=telegram_id).update(kwargs)

        try:
            db_session.commit()
        except SQLAlchemyError as ex:
            logger.error(f'Users: database commit error "{str(ex)}"')
            db_session.rollback()
            return make_response(jsonify(message=f'Bad request'), 400)

        logger.info(f'Users: The user {email} information was successfully updated')
        return make_response(jsonify(message='Информация о пользователе успешно обновлена.'), 200)

    @doc(description="Delete user record.",
         tags=['Users Control'],
         params={'Authorization': config.PARAM_HEADER_AUTH, }
         )
    @jwt_required()
    def delete(self, telegram_id):
        user = User.query.get(telegram_id)
        if not user:
            logger.info(f'Users: The user {user} not found.')
            return make_response(jsonify(message=f'Пользователь не найден.'), 400)
        db_session.delete(user)

        try:
            db_session.commit()
        except SQLAlchemyError as ex:
            logger.error(f'Users: database commit error "{str(ex)}"')
            db_session.rollback()
            return make_response(jsonify(message=f'Bad request'), 400)

        logger.info(f'Users: The user {user} successfully deleted.')
        return make_response(jsonify(message=f'Пользователь:{id} успешно удален.'), 200)
