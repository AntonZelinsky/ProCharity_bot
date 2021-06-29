from app.database import db_session
from app.models import User
from telegram import Bot, ParseMode
from bot.charity_bot import updater

import datetime
from app import config

bot = Bot(config.TELEGRAM_TOKEN)


class TelegramNotification:
    """
    This class describes the functionality for working with notifications in Telegram.
    """

    def __init__(self, has_mailing=True) -> None:
        self.has_mailing = has_mailing

    def send_notification(self, message):
        """
           Adds queue to send notification to telegram chats.

        :param message: Message to add to the sending queue
        :return:
        """

        if not self.has_mailing in ['All', 'Enabled', 'Disabled']:
            return False

        telegram_chats = []
        query = db_session.query(User.telegram_id)

        if self.has_mailing == 'Enabled':
            telegram_chats = query.filter(User.has_mailing.is_(True))

        if self.has_mailing == 'Disabled':
            telegram_chats = query.filter(User.has_mailing.is_(False))

        if self.has_mailing == 'All':
            telegram_chats = query

        chats = [chat_id for chat_id in telegram_chats]

        for i, part_chats_id in enumerate(self.__split_chats(chats, 30)):
            context = {'message': message, 'chats_id': part_chats_id}

            updater.job_queue.run_once(self.__send_to_all, i, context=context,
                                       name=f'Notification: {message.message[0:10]}')

        return True

    def __send_to_all(self, context):
        """
        Sends the message to all telegram users registered in the database.

        :param context: A dic containing the sending parameters and the message body
        :return:
        """
        job = context.job
        message = job.context['message']
        chats_id = job.context['chats_id']

        for chat_id in chats_id:
            try:
                bot.send_message(chat_id=chat_id[0], text=message.message, parse_mode=ParseMode.MARKDOWN)
            except Exception as ex:
                raise ex

        message.was_sent = True
        message.sent_date = datetime.datetime.now()
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
