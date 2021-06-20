from app import docs
from app.apis.users import UsersList, User_item
from app.apis.auth import Refresh, Register, Login, PasswordReset
from app.apis.messages import SendMessage
from app.apis.webhook import Create_categories, Create_tasks

docs.register(Login)
docs.register(Refresh)
docs.register(Register)
docs.register(PasswordReset)
docs.register(UsersList)
docs.register(User_item)
docs.register(SendMessage)
docs.register(Create_categories)
docs.register(Create_tasks)
