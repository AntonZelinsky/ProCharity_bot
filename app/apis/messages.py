from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask import jsonify, make_response
from flask_apispec import doc, use_kwargs
from marshmallow import fields
from app.database import db_session
from app.models import Message, User
from telegram import Bot, ParseMode
from bot.charity_bot import updater
import os
from dotenv import load_dotenv
import datetime
from flask_jwt_extended import jwt_required
from app import config
import time

load_dotenv()
bot = Bot(token=os.getenv('TOKEN'))


class SendTelegramNotification(Resource, MethodResource):

    @doc(description="Send messages to the bot chat",
         summary='Send messages to the bot chat',
         tags=['Messages'],
         params=config.PARAM_HEADER_AUTH)
    @use_kwargs({"message": fields.Str()})
    @jwt_required()
    def post(self, **kwargs):
        has_mailing = True
        message = kwargs.get('message')
        if not message:
            return make_response(jsonify(result='The message can not be empty.'), 400)
        message = Message(message=message)
        db_session.add(message)
        db_session.commit()
        self.add_job_queue(message=message)

        return make_response(jsonify(result=f'The message has been added to a query job'), 200)

    def add_job_queue(self, message):
        context = {'message': message}
        updater.job_queue.run_once(self.send_notification_to_all, 1, context=context,
                                   name=f'Notification:'
                                        f' {message.message[0:10]}')

    def send_notification_to_all(self, context):
        chats = [chat_id for chat_id in db_session.query(User.telegram_id).all()]
        job = context.job
        message = job.context['message']

        for chat_id in chats:
            bot.send_message(chat_id=chat_id[0], text=message.message, parse_mode=ParseMode.MARKDOWN)
            time.sleep(1)
        message.was_sent = True
        message.sent_date = datetime.datetime.now()
        db_session.commit()
