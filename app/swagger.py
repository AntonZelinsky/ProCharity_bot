from app import docs
from app.apis.users import UsersList, User_item
from app.apis.auth.refresh import Refresh
from app.apis.auth.login import Login
from app.apis.auth.password_reset import PasswordReset
from app.apis.auth.registration import UserRegister
from app.apis.auth.invitation_checker import InvitationChecker
from app.apis.auth.send_reg_invitation import SendRegistrationInvitation
from app.apis.messages import SendPushEmailMessage
docs.register(Login)
docs.register(Refresh)
docs.register(UserRegister)
docs.register(PasswordReset)
docs.register(UsersList)
docs.register(User_item)
docs.register(SendPushEmailMessage)
docs.register(SendRegistrationInvitation)
docs.register(InvitationChecker)
