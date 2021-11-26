from flask import Blueprint
from flask_restful import Api


auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/v1/auth')
auth_api = Api(auth_bp)

from . import external_users_registration
from . import login
from . import password_reset_confirm
from . import password_reset
from . import refresh
from . import registration
from . import send_registration_invite
from . import token_checker


auth_api.add_resource(external_users_registration.ExternalUserRegistration,
                      '/external_user_registration/')
auth_api.add_resource(login.Login, '/login/')
auth_api.add_resource(password_reset.PasswordReset, '/password_reset/')
auth_api.add_resource(password_reset_confirm.PasswordResetConfirm,
                      '/password_reset_confirm/')
auth_api.add_resource(refresh.Refresh, '/token_refresh/')
auth_api.add_resource(registration.UserRegister, '/register/')
auth_api.add_resource(send_registration_invite.SendRegistrationInvite,
                      '/invitation/')
auth_api.add_resource(token_checker.TokenChecker, '/token_checker/')
