from telegram import Bot, ParseMode, error
from telegram.error import Unauthorized
import datetime

from app import config
from app.database import db_session
from app.logger import bot_logger as logger
from app.models import User
from bot.charity_bot import dispatcher

bot = Bot(config.TELEGRAM_TOKEN)


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

        chats = [user for user in chats_list]

        for i, part in enumerate(self.__split_chats(chats, config.MAILING_BATCH_SIZE)):
            context = {'message': message, 'chats': part}

            dispatcher.job_queue.run_once(self.__send_message, i * 2, context=context,
                                          name=f'Notification: {message[0:10]}_{i}')

        return True

    def send_new_tasks(self, message, send_to, send_time):
        for chats_count, chats_set in enumerate(self.__split_chats(send_to, config.MAILING_BATCH_SIZE)):
            context = {'message': message, 'chats': chats_set}

            send_time = send_time + datetime.timedelta(seconds=chats_count+1)

            dispatcher.job_queue.run_once(self.__send_message, send_time, context=context,
                                          name=f'Task: {message[0:10]}_{chats_count}')
            
        return send_time

    def __send_message(self, context):
        """
        Sends the message to all telegram users registered in the database.

        :param context: A dict containing the sending parameters and the message body
        :return:
        """
        job = context.job
        message = job.context['message']
        chats = job.context['chats']

        for chats_set in self.__split_chats(chats, config.MAILING_BATCH_SIZE):
            for user in chats_set:
                self.__sending(message, user)
        logger.info("MESSAGE SENT")

    def __sending(self, message, user):
        tries = 3
        for i in range(tries):
            try:
                bot.send_message(chat_id=user.telegram_id, text=message,
                                parse_mode=ParseMode.HTML, disable_web_page_preview=True)
                logger.info(f"Send message to {user.telegram_id}")
            except error.BadRequest as ex:
                if i < tries - 1:
                    continue
                else:
                    logger.error(f'{str(ex.message)}, telegram_id: {user.telegram_id}')
            except Unauthorized as ex:
                logger.error(f'{str(ex.message)}: {user.telegram_id}')
                User.query.filter_by(telegram_id=user.telegram_id).update({'banned': True, 'has_mailing': False})
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
