import os
from flask import request
from dotenv import load_dotenv
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path)

# -----------------------
# Basic project settings
PROJECT_NAME = "ProCharrity bot"
HOST_NAME = 'host'
PASSWORD_POLICY = {
    "min_length": 8,
    "uppercase": 1,
    "max_length": 32,
}

# ------------------------
# Registration settings
SUBJECT = 'Registration'
INVITATION_TEMPLATE = 'email_templates/invitation_email.html'
# Token expiration for registering a new user in the admin panel
INV_TOKEN_EXPIRATION = 24  # hours
PUSH_TEMPLATE = 'email_templates/push_message.html'
# ------------------------------
# swagger api documentation url
SWAGGER_JSON = '/api/doc/swagger/'
SWAGGER_UI = '/api/doc/swagger-ui/'
# Parameters for authorization by Header
PARAM_HEADER_AUTH = {
    'Authorization': {
        'description':
            'HTTP header with JWT access token, like: Authorization: Bearer asdf.qwer.zxcv',
        'in': 'header',
        'type': 'string',
        'required': True
    }
}


# ------------------------------
# Basic application settings
class Config:
    # Flask Settings:
    DEBUG = True
    SITE_NAME = 'Test_site'
    SECRET_KEY = 'ASDfasdQW4)(83099498&$^%2ewf'

    # Token settings
    JWT_ACCESS_TOKEN_EXPIRES = 1800  # 30 minutes
    JWT_REFRESH_TOKEN_EXPIRES = 1800  # 30 minutes
    JWT_SECRET_KEY = 'Ad3ewrf#$wqA24&2W24-0)*&)@43'

    # DataBase settings:
    SQL_ALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')

    JSON_SORT_KEYS = False
    APISPEC_SPEC = {'APISPEC_SPEC':
                        APISpec(title=PROJECT_NAME,
                                version='v1',
                                plugins=[MarshmallowPlugin()],
                                openapi_version='2.0.0'
                                ),
                    'APISPEC_SWAGGER_URL': SWAGGER_JSON,
                    'APISPEC_SWAGGER_UI_URL': SWAGGER_UI,
                    }

    # Mail settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'tt265323@gmail.com'
    MAIL_DEFAULT_SENDER = 'tt265323@gmail.com'
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
