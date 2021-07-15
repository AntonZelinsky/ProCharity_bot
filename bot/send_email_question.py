import os

from dotenv import load_dotenv
from flask import render_template

from app import app, config
from app.messages import send_email
from app.models import User

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path)


def send_question(telegram_id, message, subject):
    recipients = [os.getenv('EMAIL_PROCHARRITY')]
    user = User.query.get(telegram_id)
    email = user.email
    name = f'{user.last_name} {user.first_name}'
    id = user.external_id
    with app.app_context():
        email_message = render_template(
            config.PROCHARRITY_TEMPLATE,
            message=message,
            id=id,
            email=email,
            name=name
        )
        send_email(
            recipients=recipients,
            subject=subject,
            template=email_message
        )
    return
