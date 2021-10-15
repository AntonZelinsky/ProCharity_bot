import uuid
from datetime import datetime, timedelta

from app import config
from app.database import db_session
from app.messages import send_email
from app.models import AdminTokenRequest
from flask import render_template, request


def send_token(email, path, subject, template):
    token_expiration = config.TOKEN_EXPIRATION
    token_expiration_date = datetime.now() + timedelta(hours=token_expiration)
    token = str(uuid.uuid4())

    record = AdminTokenRequest.query.filter_by(email=email).first()
    if record:
        record.token = token
        record.token_expiration_date = token_expiration_date
        db_session.commit()
    else:
        user = AdminTokenRequest(
            email=email,
            token=token,
            token_expiration_date=token_expiration_date
        )
        db_session.add(user)
        db_session.commit()

    link = f'{request.scheme}://{config.HOST_NAME}/#/{path}/{token}'

    email_template = render_template(
        template,
        link=link,
        expiration=token_expiration
    )
    send_email(
        recipients=[email],
        subject=subject,
        template=email_template
    )
