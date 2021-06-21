from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask import jsonify, render_template
from flask_apispec import doc, use_kwargs
from app import config
from marshmallow import fields
from app.messages import send_email
from app.database import db_session
from app.models import User


# TODO Optimize. The endpoint should use job queue
class SendPushEmailMessage(MethodResource, Resource):
    @doc(description='Send message to registered users',
         tags=["Send Push Message to users' emails"],

         )
    @use_kwargs({'message': fields.Str(), 'subject': fields.Str()})
    def post(self, **kwargs):
        message = kwargs.get('message')
        subject = kwargs.get('subject')
        template = render_template(config.PUSH_TEMPLATE, message=message)
        emails = [x.email for x in db_session.query(User).filter(User.email.isnot(None))]

        send_email(recipients=emails, subject=subject, template=template)
        return jsonify(emails)
