from flask import Flask
from app import config
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_apispec.extension import FlaskApiSpec
from password_validation import PasswordPolicy
from flask_mail import Mail
from flask_cors import CORS

jwt = JWTManager()
api = Api()
mail = Mail()
cors = CORS()
docs = FlaskApiSpec()
password_policy = PasswordPolicy(**config.PASSWORD_POLICY)


def create_app():
    app = Flask(__name__)
    app.config.update(config.APPLICATION_CONFIGURATION)
    app.config.update(**config.APISPEC_SPEC)

    from . import api, routers, swagger

    jwt.init_app(app)
    api.init_app(app)
    mail.init_app(app)
    docs.init_app(app)
    cors.init_app(app, resource={r"/*": {"origins": "*"}})

    from bot import charity_bot
    charity_bot.init()

    return app
