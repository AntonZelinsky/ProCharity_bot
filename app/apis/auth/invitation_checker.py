from flask import jsonify, make_response
from app.models import Register
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs
from marshmallow import fields
from datetime import datetime


class InvitationChecker(MethodResource, Resource):
    @doc(description='Checking invitation token.', tags=['User Registration'])
    @use_kwargs({'token': fields.Str()})
    def post(self, **kwargs):
        token = kwargs.get('token')
        record = Register.query.filter_by(token=token).first()

        if not record:
            return make_response(jsonify(message='Token is valid'), 400)

        if record.token_expiration_date < datetime.now():
            return make_response(jsonify(message='The invitation token has expired'), 400)
        return jsonify(message='Token is valid')
