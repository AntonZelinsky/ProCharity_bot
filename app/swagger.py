from app import docs
from app.apis.users import UsersList, User_item
from app.apis.auth import Refresh, Login, PasswordReset
from app.apis.registration import UserRegister, InvitationChecker
from app.apis.messages import SendMessage, SendRegistrationInvitation

docs.register(Login)
docs.register(Refresh)
docs.register(UserRegister)
docs.register(PasswordReset)
docs.register(UsersList)
docs.register(User_item)
docs.register(SendMessage)
docs.register(SendRegistrationInvitation)
docs.register(InvitationChecker)
