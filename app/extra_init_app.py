from app.apis.analytics import Analytics
from app.apis.auth.external_users_registration import ExternalUserRegistration
from app.apis.auth.invitation_checker import InvitationChecker
from app.apis.auth.login import Login
from app.apis.auth.password_reset import PasswordReset
from app.apis.auth.refresh import Refresh
from app.apis.auth.registration import UserRegister
from app.apis.auth.send_registration_invite import SendRegistrationInvite
from app.apis.categories import CreateCategories
from app.apis.health_check import HealthCheck
from app.apis.messages import SendTelegramNotification
from app.apis.tasks import CreateTasks
from app.apis.users import UsersList, UserItem


def api_extra_init(api):
    api.add_resource(UsersList, '/api/v1/users/')
    api.add_resource(UserItem, '/api/v1/users/<int:telegram_id>/')
    api.add_resource(InvitationChecker, '/api/v1/auth/invitation_checker/')
    api.add_resource(Login, '/api/v1/auth/login/')
    api.add_resource(Refresh, '/api/v1/auth/token_refresh/')
    api.add_resource(PasswordReset, '/api/v1/auth/password_reset/')
    api.add_resource(UserRegister, '/api/v1/auth/register/')
    api.add_resource(SendRegistrationInvite, '/api/v1/auth/invitation/')
    api.add_resource(ExternalUserRegistration, '/api/v1/auth/external_user_registration/')
    api.add_resource(SendTelegramNotification, '/api/v1/send_telegram_notification/')
    api.add_resource(CreateTasks, '/api/v1/tasks/')
    api.add_resource(CreateCategories, '/api/v1/categories/')
    api.add_resource(Analytics, '/api/v1/analytics/')
    api.add_resource(HealthCheck, '/api/v1/health_check/')


def swagger_extra_init(docs):
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
    docs.register(HealthCheck)
