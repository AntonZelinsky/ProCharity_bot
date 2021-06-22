from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask import jsonify, make_response
from flask_apispec import doc, use_kwargs
from marshmallow import fields
from app.database import db_session
from app.models import Message, User
import telegram
from bot.charity_bot import updater
import os
from dotenv import load_dotenv

load_dotenv()
bot = telegram.Bot(token=os.getenv('TOKEN'))


class SendTelegramMessage(Resource, MethodResource):

    @doc(description='Send message to telegram chat',
         tags=['Telegram'])
    @use_kwargs({"message": fields.Str()})
    def post(self, **kwargs):
        message = kwargs.get('message')
        if not message:
            return make_response(jsonify(result='The message can not be empty.'), 400)
        message = Message(message=message)
        db_session.add(message)
        db_session.commit()
        self.add_job_q(message=message)

        return make_response(jsonify(result=f'The message has been added to a query job'), 200)

    def add_job_q(self, message):
        chats = [user.telegram_id for user in User.query.all()]

        for chat_id in chats:
            context = {'chat_id': chat_id, 'text': message.message}
            updater.job_queue.run_once(self.alarm, 1, context=context, name=str(chat_id))

    def alarm(self, context):
        job = context.job
        chat_id = job.context['chat_id']
        text = job.context['text']
        bot.send_message(chat_id=chat_id, text=text)
