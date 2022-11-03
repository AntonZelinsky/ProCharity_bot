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
class UserMessageContext:
    message: str
    userid: int


@dataclass
class UserNotificationsContext:
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
             user_message_context = UserMessageContext(message=message, userid=user.telegram_id)
             context_list.append(user_message_context)

        user_notification_context = UserNotificationsContext(context_list)

        self.send_message(user_notification_context)

        return True

    def send_message(self, user_notification_context, send_time):
        """
        Sends the message to all telegram users registered in the database.

        :param context: A dict containing the sending parameters and the message body
        :return:
        """
        for send_count, send_set in enumerate(self.__split_chats(user_notification_context.user_message_context, config.MAILING_BATCH_SIZE)):
            send_time = send_time + datetime.timedelta(seconds=send_count+1)

            dispatcher.job_queue.run_once(self.__sending, send_time, context=send_set,
                                          name=f'Sending: {send_count}')
        return send_time

    def __sending(self, context):
        job = context.job
        for sending in job.context:
            tries = 3
            for i in range(tries):
                try:
                    bot.send_message(chat_id=sending.userid, text=sending.message,
                                    parse_mode=ParseMode.HTML, disable_web_page_preview=True)
                    logger.info(f"Sent message to {sending.userid}")
                    return
                except error.BadRequest as ex:
                    if i < tries:
                        logger.error(f'{str(ex.message)}, telegram_id: {sending.userid}')
                        logger.info(f"Retry to send after {i}")
                        time.sleep(i)
                    else:
                        logger.error(f'{str(ex.message)}, telegram_id: {sending.userid}')
                except Unauthorized as ex:
                    logger.error(f'{str(ex.message)}: {sending.userid}')
                    User.query.filter_by(telegram_id=sending.userid).update({'banned': True, 'has_mailing': False})
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
