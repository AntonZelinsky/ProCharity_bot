from app import docs
from app.auth.refresh import Refresh
from app.auth.login import Login
from app.auth.password_reset import PasswordReset
from app.auth.registration import UserRegister
from app.auth.external_users_registration import ExternalUserRegistration
from app.auth.token_checker import TokenChecker
from app.auth.send_registration_invite import SendRegistrationInvite
from app.auth.password_reset_confirm import PasswordResetConfirm
from app.front.analytics import Analytics
from app.front.users import UsersList, UserItem
from app.front.send_tg_notification import SendTelegramNotification
from app.webhooks.categories import CreateCategories
from app.webhooks.tasks import CreateTasks
from app.webhooks.health_check import HealthCheck


docs.register(Login, blueprint='auth_bp')
docs.register(Refresh, blueprint='auth_bp')
docs.register(UserRegister, blueprint='auth_bp')
docs.register(PasswordReset, blueprint='auth_bp')
docs.register(PasswordResetConfirm, blueprint='auth_bp')
docs.register(ExternalUserRegistration, blueprint='auth_bp')
docs.register(SendRegistrationInvite, blueprint='auth_bp')
docs.register(TokenChecker, blueprint='auth_bp')

docs.register(Analytics, blueprint='front_bp')
docs.register(SendTelegramNotification, blueprint='front_bp')
docs.register(UsersList, blueprint='front_bp')
docs.register(UserItem, blueprint='front_bp')

docs.register(CreateCategories, blueprint='webhooks_bp')
docs.register(CreateTasks, blueprint='webhooks_bp')
docs.register(HealthCheck, blueprint='webhooks_bp')
