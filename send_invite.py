import click
import uuid
from datetime import datetime, timedelta
from smtplib import SMTPException

from sqlalchemy.exc import SQLAlchemyError

from app import create_app
from app.database import db_session
from app import config
from app.messages import send_email
from app.models import AdminRegistrationRequest, AdminUser
from email_validator import EmailNotValidError, validate_email
from flask import render_template, request


@click.command()
@click.argument('email')
def cli(email):
    if email:
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError as ex:
            click.echo(f"Send registration invite: {str(ex)}")

    admin_user = AdminUser.query.filter_by(email=email).first()
    if admin_user:
        click.echo("Пользователь с указанным почтовым адресом уже зарегистрирован.")

    token_expiration = config.INV_TOKEN_EXPIRATION
    invitation_token_expiration_date = datetime.now() + timedelta(hours=token_expiration)
    invitation_token = str(uuid.uuid4())

    register_record = AdminRegistrationRequest.query.filter_by(email=email).first()
    try:
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

        invitation_link = f'http://{config.HOST_NAME}/#/register/{invitation_token}'
        # ЗДЕСЬ ОТПРАВКА СООБЩЕНИЯ НА ПОЧТУ


    except SQLAlchemyError as ex:
        db_session.rollback()
        click.echo(f'Bad request: {str(ex)}')

    except SMTPException as ex:
        click.echo(f"The invitation message cannot be sent.")



if __name__ == '__main__':
    cli()
