from datetime import datetime

from app.models import AdminTokenRequest
from flask import jsonify, make_response
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_restful import Resource
from marshmallow import fields
from app.logger import app_logger as logger


class TokenChecker(MethodResource, Resource):
    """Checker of invitation or password reset token"""

    @doc(description='Checking invitation token.', tags=['User Registration'],
         params={
             'token': {
                 'description': 'Invitation token',
                 'in': 'query',
                 'type': 'string',
                 'required': True
             },
         },
         responses={200: {'description': "Токен подтвержден."},
                    403: {'description': "Токен не был найден или просрочен. "
                                         "Пожалуйста свяжитесь со своим системным администратором."},

                    }
         )
    @use_kwargs({'token': fields.Str()})
    def post(self, **kwargs):
        token = kwargs.get('token')
        record = AdminTokenRequest.query.filter_by(token=token).first()

        if not record or record.token_expiration_date < datetime.now():
            logger.error(f"Token Checker: Token '{token}' not confirmed.")
            return make_response(jsonify(message="Токен не был найден или просрочен. "
                                                 "Пожалуйста свяжитесь со своим системным администратором."), 403)
        logger.info(f"Token Checker: Token for user '{record.email}' confirmed.")
        return make_response(jsonify(message='Токен подтвержден.'), 200)
