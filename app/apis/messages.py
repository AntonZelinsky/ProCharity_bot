from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask import jsonify
from flask_apispec import doc, use_kwargs
from flask_jwt_extended import jwt_required
from app import config
from marshmallow import fields


# TODO Complete push messages from admin panel
class SendMessage(MethodResource, Resource):
    @doc(description='Send message to registered users',
         tags=['Send Message'],
         params=config.PARAM_HEADER_AUTH
         )
    @use_kwargs({'message': fields.Str()})
    @jwt_required()
    def post(self):
        return jsonify(message='Message has been sent to users')
