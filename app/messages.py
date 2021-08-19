from flask_mail import Message
from app.app_init import mail


def send_email(recipients: list, subject: str, template: str) -> None:
    """
    The function of sending messages to the user's mail address

    :param recipients: Recipient list
    :param subject: Subject of email
    :param template: HTML template
    :return:
    """
    msg = Message(subject=subject, recipients=recipients, html=template)
    mail.send(msg)
