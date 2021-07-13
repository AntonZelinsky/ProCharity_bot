from app import app, config
from app.messages import send_email
from app.models import User


def send_question(telegram_id, message, subject):
    recipients = [config.EMAIL_PROCHARRITY]
    user = User.query.get(telegram_id)
    email = user.email
    name = user.last_name + ' ' + user.first_name
    id = user.external_id
    email_message = f'<p>{message}</p>\
                      <br>\
                      <p>id волонтёра - {id}</p>\
                      <p>E-mail - {email}</p>\
                      <p>Имя - {name}</p>'
    print(recipients)
    recipients = ['s.musorin@yandex.ru']
    with app.app_context():
        send_email(
            recipients=recipients,
            subject=subject,
            template=email_message
        )
    return
