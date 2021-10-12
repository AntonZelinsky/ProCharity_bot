from app import api
from app.apis.users import UsersList, UserItem
#from app.apis.categories import CreateCategories
#from app.apis.tasks import CreateTasks
from app.apis.auth.refresh import Refresh
from app.apis.auth.login import Login
from app.apis.auth.password_reset import PasswordReset
from app.apis.auth.registration import UserRegister
from app.apis.auth.external_users_registration import ExternalUserRegistration
from app.apis.auth.token_checker import TokenChecker
from app.apis.auth.send_registration_invite import SendRegistrationInvite
from app.apis.messages import SendTelegramNotification
#from app.apis.analytics import Analytics
#from app.apis.webhooks.health_check import HealthCheck
from app.apis.auth.password_reset_confirm import PasswordResetConfirm

# users endpoints
api.add_resource(UsersList, '/api/v1/users/')
api.add_resource(UserItem, '/api/v1/users/<int:telegram_id>/')
# Auth endpoints
api.add_resource(TokenChecker, '/api/v1/auth/token_checker/')
api.add_resource(Login, '/api/v1/auth/login/')
api.add_resource(Refresh, '/api/v1/auth/token_refresh/')
api.add_resource(PasswordReset, '/api/v1/auth/password_reset/')
api.add_resource(PasswordResetConfirm, '/api/v1/auth/password_reset_confirm/' )
api.add_resource(UserRegister, '/api/v1/auth/register/')
api.add_resource(SendRegistrationInvite, '/api/v1/auth/invitation/')
api.add_resource(ExternalUserRegistration, '/api/v1/auth/external_user_registration/')
# Notification
api.add_resource(SendTelegramNotification, '/api/v1/send_telegram_notification/')
# Webhooks
#api.add_resource(CreateTasks, '/api/v1/tasks/')
#api.add_resource(CreateCategories, '/api/v1/categories/')
#api.add_resource(Analytics, '/api/v1/analytics/')
#api.add_resource(HealthCheck, '/api/v1/health_check/')
