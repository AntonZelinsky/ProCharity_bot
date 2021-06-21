from app import docs
from app.apis.users import UsersList, User_item
<<<<<<< HEAD
from app.apis.auth import Refresh, Register, Login, PasswordReset
from app.apis.messages import SendMessage
from app.apis.create_categories import Create_categories
from app.apis.create_tasks import Create_tasks

=======
from app.apis.auth.refresh import Refresh
from app.apis.auth.login import Login
from app.apis.auth.password_reset import PasswordReset
from app.apis.auth.registration import UserRegister
from app.apis.auth.invitation_checker import InvitationChecker
from app.apis.auth.send_reg_invitation import SendRegistrationInvitation
from app.apis.messages import SendPushEmailMessage
>>>>>>> upstream/master
docs.register(Login)
docs.register(Refresh)
docs.register(UserRegister)
docs.register(PasswordReset)
docs.register(UsersList)
docs.register(User_item)
<<<<<<< HEAD
docs.register(SendMessage)
docs.register(Create_categories)
docs.register(Create_tasks)
=======
docs.register(SendPushEmailMessage)
docs.register(SendRegistrationInvitation)
docs.register(InvitationChecker)
>>>>>>> upstream/master
