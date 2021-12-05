from flask import Flask, request, jsonify
from flask_apispec.extension import FlaskApiSpec
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from password_validation import PasswordPolicy
from telegram import Update

from app import config
from app.config import TELEGRAM_TOKEN

jwt = JWTManager()
mail = Mail()
cors = CORS()
docs = FlaskApiSpec()
password_policy = PasswordPolicy(**config.PASSWORD_POLICY)


def create_app():
    app = Flask(__name__)
    app.config.update(config.APPLICATION_CONFIGURATION)
    app.config.update(**config.APISPEC_SPEC)

    from app.auth import swagger_auth
    from app.front import swagger_front
    from app.webhooks import swagger_webhooks

    from app.auth import auth_bp
    from app.front import front_bp
    from app.webhooks import webhooks_bp

    app.register_blueprint(webhooks_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(front_bp)

    jwt.init_app(app)
    mail.init_app(app)
    docs.init_app(app)
    cors.init_app(app, resource={r"/*": {"origins": "*"}})

    init_bot(app)

    return app


def init_bot(app):
    from bot import charity_bot
    dispatcher = charity_bot.init()

    @app.post(f'/api/{TELEGRAM_TOKEN}/telegramWebhook')
    def webhook():
        update = Update.de_json(request.json, dispatcher.bot)
        dispatcher.process_update(update)
        return jsonify({})