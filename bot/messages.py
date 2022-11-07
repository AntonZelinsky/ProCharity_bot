from telegram import Bot, ParseMode, error
from telegram.error import Unauthorized
import datetime
import time
from dataclasses import dataclass
from typing import List
import pytz

from app import config
from app.database import db_session
from app.logger import bot_logger as logger
from app.models import User
from bot.charity_bot import dispatcher

bot = Bot(config.TELEGRAM_TOKEN)


@dataclass
class SendUserMessageContext :
    message: str
    telegram_id: int


@dataclass
class SendUserNotificationsContext:
    user_message_context: List[SendUserMessageContext]


class TelegramNotification:
    """
    This class describes the functionality for working with notifications in Telegram.
    """

    def __init__(self, has_mailing: str = 'subscribed') -> None:
        self.has_mailing = has_mailing

    # TODO refactoring https://github.com/python-telegram-bot/python-telegram-bot/wiki/Avoiding-flood-limits
    def send_notification(self, message):
        """
           Adds queue to send notification to telegram chats.

        :param message: Message to add to the sending queue
        :param telegram_chats: Users query
        :return:
        """
        if self.has_mailing not in ('all', 'subscribed', 'unsubscribed'):
            return False

        chats_list = []
        query = db_session.query(User.telegram_id).filter(User.banned.is_(False))

        if self.has_mailing == 'subscribed':
            chats_list = query.filter(User.has_mailing.is_(True))

        if self.has_mailing == 'unsubscribed':
            chats_list = query.filter(User.has_mailing.is_(False))

        if self.has_mailing == 'all':
            chats_list = query

        user_notification_context = SendUserNotificationsContext([])
        for user in chats_list:
            user_message_context = SendUserMessageContext(message=message, telegram_id=user.telegram_id)
            user_notification_context.user_message_context.append(user_message_context)
            send_time = datetime.datetime.now(pytz.utc)
        send_time = self.send_batch_messages(user_notification_context, send_time)

        return True

    def send_batch_messages(self, user_notification_context, send_time):
        for send_set in self.__split_chats(user_notification_context.user_message_context, config.MAILING_BATCH_SIZE):

            for user_message_context in send_set:
                dispatcher.job_queue.run_once(self.__send_message_context, send_time, context=user_message_context,
                                              name=f'Sending: {user_message_context.message[0:10]}')
                send_time = send_time + datetime.timedelta(seconds=1)
                # self.__send_message_context(user_message_context)
        return send_time
                
    def __send_message_context(self, user_message_context):
        job = user_message_context.job
        message = job.context.message
        telegram_id = job.context.telegram_id
        tries = 3
        for i in range(tries):
            try:
                bot.send_message(chat_id=telegram_id, text=message,
                                parse_mode=ParseMode.HTML, disable_web_page_preview=True)
                logger.info(f"Sent message to {telegram_id}")
                return
            except error.BadRequest as ex:
                logger.error(f'{str(ex.message)}, telegram_id: {telegram_id}')
                if i < tries:
                    logger.info(f"Retry to send after {i}")
                    time.sleep(i)
            except Unauthorized as ex:
                logger.error(f'{str(ex.message)}: {telegram_id}')
                User.query.filter_by(telegram_id=telegram_id).update({'banned': True, 'has_mailing': False})
                db_session.commit()

    @staticmethod
    def __split_chats(array, size):

        arrs = []
        while len(array) > size:
            piece = array[:size]
            arrs.append(piece)
            array = array[size:]
        arrs.append(array)
        return arrs
