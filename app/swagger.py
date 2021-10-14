from app import docs
from app.apis.users.users import UsersList, UserItem
from app.apis.auth.refresh import Refresh
from app.apis.auth.login import Login
from app.apis.auth.password_reset import PasswordReset
from app.apis.auth.registration import UserRegister
from app.apis.auth.external_users_registration import ExternalUserRegistration
from app.apis.auth.token_checker import TokenChecker
from app.apis.auth.send_registration_invite import SendRegistrationInvite
from app.apis.notifications.send_tg_notification import SendTelegramNotification
from app.apis.webhooks.categories import CreateCategories
from app.apis.webhooks.tasks import CreateTasks
from app.apis.webhooks.analytics import Analytics
from app.apis.webhooks.health_check import HealthCheck
from app.apis.auth.password_reset_confirm import PasswordResetConfirm

docs.register(Login, blueprint='auth_bp')
docs.register(Refresh, blueprint='auth_bp')
docs.register(UserRegister, blueprint='auth_bp')
docs.register(PasswordReset, blueprint='auth_bp')
docs.register(PasswordResetConfirm, blueprint='auth_bp')
docs.register(ExternalUserRegistration, blueprint='auth_bp')
docs.register(SendRegistrationInvite, blueprint='auth_bp')
docs.register(TokenChecker, blueprint='auth_bp')

docs.register(UsersList, blueprint='users_bp')
docs.register(UserItem, blueprint='users_bp')

docs.register(SendTelegramNotification, blueprint='notifications_bp')

docs.register(CreateCategories, blueprint='webhooks_bp')
docs.register(CreateTasks, blueprint='webhooks_bp')
docs.register(Analytics, blueprint='webhooks_bp')
docs.register(HealthCheck, blueprint='webhooks_bp')
