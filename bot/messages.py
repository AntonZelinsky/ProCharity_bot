from app.database import db_session
from app.models import User
from telegram import Bot, ParseMode, error
from bot.charity_bot import updater, logger

from app import config

bot = Bot(config.TELEGRAM_TOKEN)


class TelegramNotification:
    """
    This class describes the functionality for working with notifications in Telegram.
    """

    def __init__(self, has_mailing: str = 'subscribed') -> None:
        self.has_mailing = has_mailing

    # TODO refactoring https://github.com/python-telegram-bot/python-telegram-bot/wiki/Avoiding-flood-limits
    def send_notification(self, message, send_to=None):
        """
           Adds queue to send notification to telegram chats.

        :param message: Message to add to the sending queue
        :param telegram_chats: Users query
        :return:
        """
        if self.has_mailing not in ('all', 'subscribed', 'unsubscribed'):
            return False

        query = db_session.query(User.telegram_id)

        if self.has_mailing == 'subscribed':
            send_to = query.filter(User.has_mailing.is_(True))

        if self.has_mailing == 'unsubscribed':
            send_to = query.filter(User.has_mailing.is_(False))

        if self.has_mailing == 'all':
            send_to = query

        chats = [user for user in send_to]

        for i, part in enumerate(self.__split_chats(chats, config.NUMBER_USERS_TO_SEND)):
            context = {'message': message, 'chats': part}

            updater.job_queue.run_once(self.__send_message, i, context=context,
                                       name=f'Notification: {message[0:10]}_{i}')

        return True

    def send_new_tasks(self, message, send_to):

        for i, part in enumerate(self.__split_chats(send_to, config.NUMBER_USERS_TO_SEND)):
            context = {'message': message, 'chats': part}

            updater.job_queue.run_once(self.__send_message, i, context=context,
                                       name=f'Task: {0:10}_{i}')

    def __send_message(self, context):
        """
        Sends the message to all telegram users registered in the database.

        :param context: A dict containing the sending parameters and the message body
        :return:
        """
        job = context.job
        message = job.context['message']
        chats = job.context['chats']

        for user in chats:
            try:
                bot.send_message(chat_id=user.telegram_id, text=message, parse_mode=ParseMode.HTML)
            except error.BadRequest as ex:
                logger.error(str(ex), user.telegram_id)

    @staticmethod
    def __split_chats(array, size):

        arrs = []
        while len(array) > size:
            piece = array[:size]
            arrs.append(piece)
            array = array[size:]
        arrs.append(array)
        return arrs
