from app import api
from app.api import Login, Register, Users, Refresh
from app.webhook import Create_categories, Create_tasks

api.add_resource(Users, '/api/users/')
api.add_resource(Register, '/api/register/')
api.add_resource(Login, '/api/auth/login/')
api.add_resource(Refresh, '/api/auth/token_refresh/')
api.add_resource(Create_tasks, '/api/v1/tasks/')
api.add_resource(Create_categories, '/api/v1/categories/')