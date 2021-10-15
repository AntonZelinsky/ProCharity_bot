from app import docs
from app.auth.refresh import Refresh
from app.auth.login import Login
from app.auth.password_reset import PasswordReset
from app.auth.registration import UserRegister
from app.auth.external_users_registration import ExternalUserRegistration
from app.auth.token_checker import TokenChecker
from app.auth.send_registration_invite import SendRegistrationInvite
from app.auth.password_reset_confirm import PasswordResetConfirm

docs.register(Login, blueprint='auth_bp')
docs.register(Refresh, blueprint='auth_bp')
docs.register(UserRegister, blueprint='auth_bp')
docs.register(PasswordReset, blueprint='auth_bp')
docs.register(PasswordResetConfirm, blueprint='auth_bp')
docs.register(ExternalUserRegistration, blueprint='auth_bp')
docs.register(SendRegistrationInvite, blueprint='auth_bp')
docs.register(TokenChecker, blueprint='auth_bp')
