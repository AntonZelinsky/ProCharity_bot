from app.models import User
from app.database import db_session
from flask import Flask
from app import config
from app.config import Config
from app.config import PASSWORD_POLICY
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_apispec.extension import FlaskApiSpec
from password_validation import PasswordPolicy
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)
api = Api(app)
mail = Mail(app)
password_policy = PasswordPolicy(**PASSWORD_POLICY)

app.config.update(**Config.APISPEC_SPEC)

docs = FlaskApiSpec(app)

from . import api, routers, swagger
