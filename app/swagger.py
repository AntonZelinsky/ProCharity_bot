from app import docs
from app.api import Refresh, Register, Login, UsersList, User_item

docs.register(Register)
docs.register(Login)
docs.register(Refresh)
docs.register(UsersList)
docs.register(User_item)
