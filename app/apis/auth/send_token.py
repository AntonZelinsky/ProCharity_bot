import uuid
from datetime import datetime, timedelta
from smtplib import SMTPException

from sqlalchemy.exc import SQLAlchemyError

from app import config
from app.database import db_session
from app.messages import send_email
from app.models import AdminTokenRequest, AdminUser
from email_validator import EmailNotValidError, validate_email
from flask import jsonify, make_response, render_template, request
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from marshmallow import fields
from app.logger import app_logger as logger



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

