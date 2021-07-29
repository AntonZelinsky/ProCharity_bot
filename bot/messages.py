from telegram import Bot, ParseMode, error
from telegram.error import Unauthorized

from app import config
from app.database import db_session
from app.models import User
from bot.charity_bot import updater, logger

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
        query = db_session.query(User.telegram_id)

        if self.has_mailing == 'subscribed':
            chats_list = query.filter(User.has_mailing.is_(True))

        if self.has_mailing == 'unsubscribed':
            chats_list = query.filter(User.has_mailing.is_(False))

        if self.has_mailing == 'all':
            chats_list = query

        chats = [user for user in chats_list]

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
                logger.error(f'{str(ex.message)}, telegram_id: {user.telegram_id}')
            except Unauthorized as ex:
                logger.error(f'{str(ex.message)}: {user.telegram_id}')
                User.query.filter_by(telegram_id=user.telegram_id).update({'has_mailing': False})
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
