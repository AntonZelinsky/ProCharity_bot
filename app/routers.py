from app import api
from app.apis.users import UsersList, User_item
from app.apis.auth import Refresh, Register, Login, PasswordReset
from app.apis.messages import SendMessage
from app.api import Login, Register, Users, Refresh
from app.webhook import Create_categories, Create_tasks

api.add_resource(UsersList, '/api/users/')
api.add_resource(User_item, '/api/users/<int:id>/')
api.add_resource(Register, '/api/register/')
api.add_resource(Login, '/api/auth/login/')
api.add_resource(Refresh, '/api/auth/token_refresh/')
api.add_resource(PasswordReset, '/api/auth/password_reset/')
api.add_resource(SendMessage, '/api/send_message/')
api.add_resource(Create_tasks, '/api/v1/tasks/')
api.add_resource(Create_categories, '/api/v1/categories/')
