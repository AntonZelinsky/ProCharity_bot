from app.models import User
from app.database import db_session
from flask import Flask
from app import config
from app.config import PASSWORD_POLICY
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_apispec.extension import FlaskApiSpec
from password_validation import PasswordPolicy
from flask_mail import Mail
from flask_cors import CORS


app = Flask(__name__)
app.config.update(config.APPLICATION_CONFIGURATION)
cors = CORS(app, resource={r"/*": {"origins": "*"}})

jwt = JWTManager(app)
api = Api(app)
mail = Mail(app)
password_policy = PasswordPolicy(**PASSWORD_POLICY)

app.config.update(**config.APISPEC_SPEC)

docs = FlaskApiSpec(app)

from . import api, routers, swagger
from bot.charity_bot import main
main()  # bot  initialization
