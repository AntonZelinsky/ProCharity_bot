from app.app_init import docs
from app.apis.users import UsersList, UserItem
from app.apis.auth.refresh import Refresh
from app.apis.auth.login import Login
from app.apis.auth.password_reset import PasswordReset
from app.apis.auth.registration import UserRegister
from app.apis.auth.external_users_registration import ExternalUserRegistration
from app.apis.auth.invitation_checker import InvitationChecker
from app.apis.auth.send_registration_invite import SendRegistrationInvite
from app.apis.messages import SendTelegramNotification
from app.apis.categories import CreateCategories
from app.apis.tasks import CreateTasks
from app.apis.analytics import Analytics


docs.register(Login)
docs.register(Refresh)
docs.register(UserRegister)
docs.register(PasswordReset)
docs.register(UsersList)
docs.register(UserItem)
docs.register(SendRegistrationInvite)
docs.register(InvitationChecker)
docs.register(SendTelegramNotification)
docs.register(CreateCategories)
docs.register(CreateTasks)
docs.register(Analytics)
docs.register(ExternalUserRegistration)

