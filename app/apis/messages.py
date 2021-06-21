from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask import jsonify, render_template
from flask_apispec import doc, use_kwargs
from app import config
from marshmallow import fields
from app.messages import send_email
from app.database import db_session
from app.models import User


class SendTelegramMessage(Resource, MethodResource):
    pass