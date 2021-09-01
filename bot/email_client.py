import os
from smtplib import SMTPException

from flask import current_app, render_template
from flask_mail import Message

# from app import app, config, mail
from app import config, mail
from app.models import User
from app.logger import bot_logger as logger

SUBJECT_FEEDBACK = {
    'category': 'Запрос на новые компетенции',
    'question': 'Вопрос из бота',
    'feature': 'Запрос на новый функционал для бота'
}


def send_email(telegram_id, message, subject):
    app = current_app._get_current_object()
    recipients = [os.getenv('EMAIL_PROCHARRITY')]
    user = User.query.get(telegram_id)
    email = user.email
    name = f'{user.last_name} {user.first_name}'
    id = user.external_id
    with app.app_context():
        template = render_template(
            config.PROCHARRITY_TEMPLATE,
            message=message,
            id=id,
            telegram_id=telegram_id,
            email=email,
            name=name
        )
        msg = Message(
            subject=SUBJECT_FEEDBACK[subject],
            recipients=recipients,
            html=template
        )
        try:
            mail.send(msg)
        except SMTPException as ex:  # base smtplib exception
            logger.error(f"Email client: {str(ex)}")
    return
