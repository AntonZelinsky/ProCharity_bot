import datetime

from flask import jsonify, make_response
from flask_apispec import doc, use_kwargs
from flask_apispec.views import MethodResource
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from marshmallow import Schema, fields
from sqlalchemy.exc import SQLAlchemyError

from app import config
from app.database import db_session
from app.error_handlers import InvalidAPIUsage
from app.logger import app_logger as logger
from app.models import Notification
from bot.messages import TelegramMessage


class TelegramMessageSchema(Schema):
    message = fields.String(required=True)


class SendTelegramMessage(Resource, MethodResource):

    @doc(description='Sends message to the telegram user.'
                     'Requires "message" and "telegram_id" parameters.',
         summary='Send telegram messages to the bot chat',
         tags=['Messages'],
         responses={
             200: {'description': 'The message has been sent'},
             400: {'description': 'The message can not be empty'},
         },
         params={
             'message': {
                 'description': 'Message to user. Max len 4096',
                 'in': 'query',
                 'type': 'string',
                 'required': True
             },
             'telegram_id': {
                 'description': (
                    'Sending notification to user with this telegram id'
                  ),
                 'in': 'path',
                 'type': 'integer',
                 'required': True
             },
             'Authorization': config.PARAM_HEADER_AUTH,
         }
         )
    @use_kwargs(TelegramMessageSchema)
    @jwt_required()
    def post(self, telegram_id, **kwargs):
        message = kwargs.get('message').replace('&nbsp;', '')

        if not message:
            logger.info(
                'Messages: The <message> parameter have not been passed'
                )
            return make_response(
                jsonify(
                    result=(
                        'Необходимо указать параметр <message>.'
                    )
                ), 400
                )

        authorized_user = get_jwt_identity()
        message = Notification(message=message, sent_by=authorized_user)
        db_session.add(message)
        try:
            db_session.commit()
            mes = TelegramMessage(telegram_id)
            mes.send_message(message=message.message)
            message.was_sent = True
            message.sent_date = datetime.datetime.now()
            db_session.commit()
        except InvalidAPIUsage as ex:
            return make_response(
                jsonify(result=ex.message), ex.status_code
            )
        except SQLAlchemyError as ex:
            logger.error(f'Messages: Database commit error "{str(ex)}"')
            db_session.rollback()
            return make_response(
                jsonify(message=f'Bad request: {str(ex)}'), 400
            )

        logger.info(f'Messages: The message "{message.message}" '
                    'has been successfully sent to user')
        return make_response(
            jsonify(
                result="Сообщение успешно отправлено пользователю."
            ), 200
        )
