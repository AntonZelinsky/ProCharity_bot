from datetime import datetime

from app.models import Register
from flask import jsonify, make_response
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_restful import Resource
from marshmallow import fields


class InvitationChecker(MethodResource, Resource):
    """Checker of invitation token"""

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
                    403: {'description': "Приглашение не было найдено или просрочено. "
                                         "Пожалуйста свяжитесь с своим системным администратором."},

                    }
         )
    @use_kwargs({'token': fields.Str()})
    def post(self, **kwargs):
        token = kwargs.get('token')
        record = Register.query.filter_by(token=token).first()

        if not record or record.token_expiration_date < datetime.now():
            return make_response(jsonify(message="Приглашение не было найдено или просрочено. "
                                                 "Пожалуйста свяжитесь с своим системным администратором."), 403)

        return make_response(jsonify(message='Токен подтвержден.'), 200)
