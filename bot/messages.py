from app.database import db_session
from app.models import User
from telegram import Bot, ParseMode
from bot.charity_bot import updater

import datetime
from app import config
import time

bot = Bot(config.TELEGRAM_TOKEN)


class TelegramNotification:
    """
    This class describes the functionality for working with notifications in Telegram.
    """

    def __init__(self, has_mailing: bool = True) -> None:
        self.has_mailing = has_mailing

    def send_notification(self, message):
        """
           Adds queue to send notification to telegram chats.

        :param message: Message to add to the sending queue
        :return:
        """
        context = {'message': message, 'has_mailing': self.has_mailing, }

        updater.job_queue.run_once(self.__send_to_all, 1, context=context,
                                   name=f'Notification: {message.message[0:10]}')

    def __send_to_all(self, context):
        """
        Sends the message to all telegram users registered in the database.

        :param context: A dic containing the sending parameters and the message body
        :return:
        """
        job = context.job
        has_mailing = job.context['has_mailing']
        chats = [chat_id for chat_id in db_session.query(User.telegram_id).
            filter(User.has_mailing.is_(has_mailing)).all()]

        message = job.context['message']

        for chat_id in chats:
            bot.send_message(chat_id=chat_id[0], text=message.message, parse_mode=ParseMode.MARKDOWN)
            time.sleep(1)
        # marks the sent message as 'sent' and add date of sending.
        message.was_sent = True
        message.sent_date = datetime.datetime.now()
        db_session.commit()
