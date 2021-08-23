from flask import Flask
from app import config
from app.config import PASSWORD_POLICY
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_apispec.extension import FlaskApiSpec
from password_validation import PasswordPolicy
from flask_mail import Mail
from flask_cors import CORS


cors = CORS()
jwt = JWTManager()
api = Api()
mail = Mail()
password_policy = PasswordPolicy(**PASSWORD_POLICY)
docs = FlaskApiSpec()


def create_app():
    app = Flask(__name__)
    app.config.update(config.APPLICATION_CONFIGURATION)
    
    cors.init_app(app, resource={r"/*": {"origins": "*"}})
    jwt.init_app(app)
    api.init_app(app)
    mail.init_app(app)

    app.config.update(**config.APISPEC_SPEC)

    docs.init_app(app)
    
    from . import apis, routers, swagger
    from bot import charity_bot
    charity_bot.init()
    
    return app
