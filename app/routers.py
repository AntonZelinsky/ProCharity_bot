from app import api
from app.apis.users import UsersList, User_item
from app.apis.categories import CreateCategories
from app.apis.tasks import CreateTasks
from app.apis.auth.refresh import Refresh
from app.apis.auth.login import Login
from app.apis.auth.password_reset import PasswordReset
from app.apis.auth.registration import UserRegister, ExternalUserRegistration
from app.apis.auth.invitation_checker import InvitationChecker
from app.apis.auth.send_reg_invitation import SendRegistrationInvite
from app.apis.messages import SendTelegramNotification
from app.apis.analysis import Analysis


# users endpoints
api.add_resource(UsersList, '/api/v1/users/')
api.add_resource(User_item, '/api/v1/users/<int:id>/')
# Auth endpoints
api.add_resource(InvitationChecker, '/api/v1/auth/invitation_checker/')
api.add_resource(Login, '/api/v1/auth/login/')
api.add_resource(Refresh, '/api/v1/auth/token_refresh/')
api.add_resource(PasswordReset, '/api/v1/auth/password_reset/')
api.add_resource(UserRegister, '/api/v1/auth/register/')
api.add_resource(SendRegistrationInvite, '/api/v1/auth/invitation/')
api.add_resource(ExternalUserRegistration, '/api/v1/auth/external_user_registration/')
# Notification
api.add_resource(SendTelegramNotification, '/api/v1/send_telegram_notification/')
# Webhooks
api.add_resource(CreateTasks, '/api/v1/tasks/')
api.add_resource(CreateCategories, '/api/v1/categories/')
api.add_resource(Analysis, '/api/v1/analysis/')
