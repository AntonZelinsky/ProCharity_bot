from app import docs
from app.apis.users import UsersList, User_item
from app.apis.auth import Refresh, Register, Login, PasswordReset
from app.apis.messages import SendMessage

docs.register(Login)
docs.register(Refresh)
docs.register(Register)
docs.register(PasswordReset)
docs.register(UsersList)
docs.register(User_item)
docs.register(SendMessage)