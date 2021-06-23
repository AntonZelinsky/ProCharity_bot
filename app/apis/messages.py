from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask import jsonify, make_response

from flask_apispec import doc, use_kwargs
from marshmallow import fields, Schema
from app.database import db_session
from app.models import Message, User
from telegram import Bot, ParseMode
from bot.charity_bot import updater

import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import config
import time

bot = Bot(config.TELEGRAM_TOKEN)


class TelegramNotificationSchema(Schema):
    message = fields.String(required=True)
    chat_id = fields.Integer(required=False)
    has_mailing = fields.Boolean(required=False, default=True)


class SendTelegramNotification(Resource, MethodResource):

    @doc(description="Send messages to the bot chat",
         summary='Send messages to the bot chat',
         tags=['Messages'],
         responses={
             200: {'description': 'The message has been added to a query job'},
             400: {'description': 'The message can not be empty'},
         },
         params=config.PARAM_HEADER_AUTH,

         )
    @use_kwargs(TelegramNotificationSchema)
    @jwt_required()
    def post(self, **kwargs):

        message = kwargs.get('message')
        has_mailing = kwargs.get('has_mailing', True)
        chat_id = kwargs.get('chat_id')
        if not message:
            return make_response(jsonify(result='The message can not be empty.'), 400)

        message = Message(message=message)
        db_session.add(message)
        db_session.commit()
        self.add_job_queue(message=message,
                           has_mailing=has_mailing,
                           chat_id=chat_id)

        return make_response(jsonify(result=f'The message has been added to a query job'), 200)

    def add_job_queue(self, message, has_mailing, chat_id):

        if chat_id:
            context = {'message': message, 'chat_id': chat_id}
            updater.job_queue.run_once(self.send_notification_to_one, 1, context=context,
                                       name=f'Notification: {message.message[0:10]}')
        else:
            context = {'message': message, 'has_mailing': has_mailing, }
            updater.job_queue.run_once(self.send_notification_to_all, 1, context=context,
                                       name=f'Notification:'
                                            f' {message.message[0:10]}')

    def send_notification_to_all(self, context):
        job = context.job
        has_mailing = job.context['has_mailing']
        chats = [chat_id for chat_id in db_session.query(User.telegram_id).
            filter(User.has_mailing.is_(has_mailing)).all()]

        message = job.context['message']

        for chat_id in chats:
            bot.send_message(chat_id=chat_id[0], text=message.message, parse_mode=ParseMode.MARKDOWN)
            time.sleep(1)
        message.was_sent = True
        message.sent_date = datetime.datetime.now()
        db_session.commit()

    def send_notification_to_one(self, context):
        job = context.job
        chat_id = job.context['chat_id']
        message = job.context['message']
        bot.send_message(chat_id=chat_id, text=message.message, parse_mode=ParseMode.MARKDOWN)
        message.was_sent = True
        message.sent_date = datetime.datetime.now()
        db_session.commit()
