import os

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(BASE_DIR, '.env'))

# -----------------------
# Basic project settings
PROJECT_NAME = 'ProCharity bot'

POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

SQL_ALCHEMY_DATABASE_URL = \
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

HOST_NAME = os.getenv('HOST_NAME')

PASSWORD_POLICY = {
    'min_length': 8,
    'uppercase': 1,
    'lowercase': 1,
    'max_length': 32,
}
# procharity send email settings
PROCHARRITY_TEMPLATE = 'email_templates/send_question.html'

# ------------------------
# Registration settings
REGISTRATION_SUBJECT = 'Регистрация на портале ProCharity bot'
INVITATION_TEMPLATE = 'email_templates/invitation_email.html'

PASSWORD_RESET_SUBJECT = 'Password Reset'
PASSWORD_RESET_TEMPLATE = 'email_templates/password_reset.html'
# Token expiration for registering a new user in the admin panel
TOKEN_EXPIRATION = 24  # hours
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
WEBHOOK_URL = f'{HOST_NAME}/api/{TELEGRAM_TOKEN}/telegramWebhook'
USE_WEBHOOK = os.getenv('USE_WEBHOOK')
MAILING_BATCH_SIZE = 5

BOT_FILE_DIR = BASE_DIR + '/bot_persistence_file/'
BOT_PERSISTENCE_FILE = os.path.join(BOT_FILE_DIR, 'bot_persistence_data')

APISPEC_SPEC = {
    'APISPEC_SPEC':
        APISpec(title=PROJECT_NAME,
                version='v1',
                plugins=[MarshmallowPlugin()],
                openapi_version='2.0.0'
                ),
    'APISPEC_SWAGGER_URL': SWAGGER_JSON,
    'APISPEC_SWAGGER_UI_URL': SWAGGER_UI,

}

APPLICATION_CONFIGURATION = {
    'SECRET_KEY': 'ASDfasdQW4)(83099498&$^%2ewf',
    # Token settings
    'JWT_ACCESS_TOKEN_EXPIRES': 86400,  # 1 day
    'JWT_REFRESH_TOKEN_EXPIRES': 172800,  # 2 days
    'JWT_SECRET_KEY': 'Ad3ewrf#$wqA24&2W24-0)*&)@43',
    'PROPAGATE_EXCEPTIONS': True,
    # API rest settings
    'JSON_SORT_KEYS': False,

    # Mail settings
    'MAIL_SERVER': os.getenv('MAIL_SERVER'),
    'MAIL_PORT': os.getenv('MAIL_PORT'),
    'MAIL_USE_TLS': os.getenv('MAIL_USE_TLS'),
    'MAIL_USERNAME': os.getenv('MAIL_USERNAME'),
    'MAIL_DEFAULT_SENDER': os.getenv('MAIL_DEFAULT_SENDER'),
    'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD'),
}

# -----------------------
# Logging settings
LOG_DIR = 'logs'
LOG_PATH = os.path.join(BASE_DIR, LOG_DIR)

ACCESS_TOKEN_FOR_PROCHARITY = os.getenv('ACCESS_TOKEN_FOR_PROCHARITY')
