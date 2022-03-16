import smtplib
import click
import uuid

from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPException
from sqlalchemy.exc import SQLAlchemyError

from app import config
from app.database import db_session
from app.models import AdminRegistrationRequest, AdminUser
from email_validator import EmailNotValidError, validate_email


@click.group()
def cli():
    pass

@click.command()
@click.argument('email')
def send_invite(email):
    try:
        validate_email(email, check_deliverability=False)
    except EmailNotValidError as ex:
        return click.echo(f"Send registration invite: {str(ex)}")
    try:
        admin_user = AdminUser.query.filter_by(email=email).first()
        if admin_user:
            return click.echo("Пользователь с указанным почтовым адресом уже зарегистрирован.")

        token_expiration = config.INV_TOKEN_EXPIRATION
        invitation_token_expiration_date = datetime.now() + timedelta(hours=token_expiration)
        invitation_token = str(uuid.uuid4())

        register_record = AdminRegistrationRequest.query.filter_by(email=email).first()
    
        if register_record:
            register_record.token = invitation_token
            register_record.token_expiration_date = invitation_token_expiration_date
            db_session.commit()
        else:
            user = AdminRegistrationRequest(
                email=email,
                token=invitation_token,
                token_expiration_date=invitation_token_expiration_date
                )
            db_session.add(user)
            db_session.commit()

        invitation_link = f'https://{config.HOST_NAME}/#/register/{invitation_token}'

        send_email(email, invitation_link, token_expiration)
                   
        return click.echo("Successfully sent email")

    except SQLAlchemyError as ex:
        db_session.rollback()
        return click.echo(f'Bad request: {str(ex)}')

    except SMTPException as ex:
        return click.echo(f"The invitation message cannot be sent.")


def send_email(email, invitation_link, token_expiration):
    addr_from = config.APPLICATION_CONFIGURATION.get('MAIL_DEFAULT_SENDER')
    addr_to = email
    password = config.APPLICATION_CONFIGURATION.get('MAIL_PASSWORD')
    msg = MIMEMultipart()
    msg['From'] = addr_from
    msg['To'] = addr_to
    msg['Subject'] = f'Регистрация на портале ProCharrity bot'
    body = f'<p>Для регистрации на портале пройдите по ссылке -->>> <a href="{ invitation_link }">Регистрация</a>.</p><br>' \
           f'<p>Ссылка будет доступна в течение { token_expiration } часов</p>'
    msg.attach(MIMEText(body, 'html'))
    server = smtplib.SMTP(config.APPLICATION_CONFIGURATION.get('MAIL_SERVER'),
                          config.APPLICATION_CONFIGURATION.get('MAIL_PORT'))            
    server.starttls()
    server.login(addr_from, password)
    server.send_message(msg)
    server.quit()


cli.add_command(send_invite)

if __name__ == '__main__':
    cli()
