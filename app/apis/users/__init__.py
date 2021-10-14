from flask import Blueprint
from flask_restful import Api


users_bp = Blueprint('users_bp', __name__, url_prefix='/api/v1/users')
users_api = Api(users_bp)

from . import users

users_api.add_resource(users.UsersList, '/')
users_api.add_resource(users.UserItem, '/<int:telegram_id>/')
