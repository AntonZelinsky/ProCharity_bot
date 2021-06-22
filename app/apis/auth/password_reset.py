import random
import string

from app import config
from app.database import db_session
from app.messages import send_email
from app.models import UserAdmin
from flask import jsonify, make_response, render_template
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_restful import Resource
from marshmallow import fields
from werkzeug.security import generate_password_hash


class PasswordReset(MethodResource, Resource):
    """
    Provides password reset for admin users accounts
    The new password is sent to the registered email address.
    """

    @doc(description="Reset user's password",
         tags=['Password Reset'])
    @use_kwargs({'email': fields.Email()})
    def post(self, **kwargs):
        email = kwargs.get('email')
        user = UserAdmin.query.filter_by(email=email).first()

        if not user:
            return make_response(jsonify(message='New password has been sent'), 400)
        password = self.random_password()

        subject = 'Password Reset'
        template = render_template(config.PASSWORD_RESET_TEMPLATE, password=password)

        user.password = generate_password_hash(password=password)
        db_session.commit()
        send_email(subject=subject, template=template, recipients=[user.email])
        return make_response(jsonify(message='New password has been sent to the registered email address.'), 200)

    def random_password(self):
        length = config.PASSWORD_POLICY["min_length"]
        chars = string.ascii_letters + string.digits + '!@#$%^&*()'
        rnd = random.SystemRandom()
        return ''.join(rnd.choice(chars) for i in range(length))
