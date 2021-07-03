import os
from dotenv import load_dotenv
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path)

# -----------------------
# Basic project settings
SQL_ALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')
PROJECT_NAME = "ProCharrity bot"
HOST_NAME = '178.154.202.217'
PASSWORD_POLICY = {
    "min_length": 8,
    "uppercase": 1,
    "max_length": 32,
}

# ------------------------
# Registration settings
REGISTRATION_SUBJECT = 'Registration'
INVITATION_TEMPLATE = 'email_templates/invitation_email.html'

PASSWORD_RESET_SUBJECT = 'Password Reset'
PASSWORD_RESET_TEMPLATE = 'email_templates/password_reset.html'
# Token expiration for registering a new user in the admin panel
INV_TOKEN_EXPIRATION = 24  # hours
# ------------------------------
# swagger api documentation url
SWAGGER_JSON = '/api/doc/swagger/'
SWAGGER_UI = '/api/doc/swagger-ui/'
# Parameters for authorization by Header
PARAM_HEADER_AUTH = {
    'description': 'HTTP header with JWT access token, like: Authorization: Bearer asdf.qwer.zxcv',
    'in': 'header',
    'type': 'string',
    'required': True
}
# ------------------------------
# Pagination
PAGE_LIMIT = 10
# ------------------------------
# Telegram bot settings
TELEGRAM_TOKEN = os.getenv('TOKEN')
NUMBER_USERS_TO_SEND = 30
# ------------------------------
# Basic application settings

APPLICATION_CONFIGURATION = {
    'SITE_NAME': 'Test_site',
    'SECRET_KEY': 'ASDfasdQW4)(83099498&$^%2ewf',

    # Token settings
    'JWT_ACCESS_TOKEN_EXPIRES': 86400,  # 1 day
    'JWT_REFRESH_TOKEN_EXPIRES': 172800,  # 2 days
    'JWT_SECRET_KEY': 'Ad3ewrf#$wqA24&2W24-0)*&)@43',
    'PROPAGATE_EXCEPTIONS': True,
    # API rest settings
    'JSON_SORT_KEYS': False,

    # Mail settings
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 587,
    'MAIL_USE_TLS': True,
    'MAIL_USERNAME': 'tt265323@gmail.com',
    'MAIL_DEFAULT_SENDER': 'tt265323@gmail.com',
    'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),

}

APISPEC_SPEC = {'APISPEC_SPEC':
                    APISpec(title=PROJECT_NAME,
                            version='v1',
                            plugins=[MarshmallowPlugin()],
                            openapi_version='2.0.0'
                            ),
                'APISPEC_SWAGGER_URL': SWAGGER_JSON,
                'APISPEC_SWAGGER_UI_URL': SWAGGER_UI,

                }
