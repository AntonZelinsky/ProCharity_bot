from app import api
from app.api import Login, Register, UsersList, Refresh, User_item


api.add_resource(UsersList, '/api/users/')
api.add_resource(User_item, '/api/users/<string:username>/')
api.add_resource(Register, '/api/register/')
api.add_resource(Login, '/api/auth/login/')
api.add_resource(Refresh, '/api/auth/token_refresh/')
