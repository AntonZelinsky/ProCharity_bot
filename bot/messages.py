from telegram import Bot, ParseMode, error
from telegram.error import Unauthorized
import datetime
import time
from dataclasses import dataclass

from app import config
from app.database import db_session
from app.logger import bot_logger as logger
from app.models import User
from bot.charity_bot import dispatcher

bot = Bot(config.TELEGRAM_TOKEN)


@dataclass
class SendUserMessageContext :
    message: str
    userid: int


@dataclass
class SendUserNotificationsContext:
    user_message_context: list


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

        context_list = []
        for user in chats_list:
             user_message_context = SendUserMessageContext(message=message, userid=user.telegram_id)
             context_list.append(user_message_context)

        user_notification_context = SendUserNotificationsContext(context_list)

        self.SendBatchMessages(user_notification_context)

        return True

    def SendBatchMessages(self, user_notification_context):
        for send_set in self.__split_chats(user_notification_context.user_message_context, config.MAILING_BATCH_SIZE):

            for user_message_context in send_set:
                self.__send_message_context(user_message_context)
            time.sleep(1)
                
    def __send_message_context(self, user_message_context):
        tries = 3
        for i in range(tries):
            try:
                bot.send_message(chat_id=user_message_context.userid, text=user_message_context.message,
                                parse_mode=ParseMode.HTML, disable_web_page_preview=True)
                logger.info(f"Sent message to {user_message_context.userid}")
                return
            except error.BadRequest as ex:
                logger.error(f'{str(ex.message)}, telegram_id: {user_message_context.userid}')
                if i < tries:
                    logger.info(f"Retry to send after {i}")
                    time.sleep(i)
            except Unauthorized as ex:
                logger.error(f'{str(ex.message)}: {user_message_context.userid}')
                User.query.filter_by(telegram_id=user_message_context.userid).update({'banned': True, 'has_mailing': False})
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
