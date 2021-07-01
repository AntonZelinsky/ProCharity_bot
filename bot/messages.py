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
    def send_notification(self, message, query=None):
        """
           Adds queue to send notification to telegram chats.

        :param message: Message to add to the sending queue
        :param query: Users query
        :return:
        """

        if self.has_mailing not in ('all', 'subscribed', 'unsubscribed'):
            return False

        telegram_chats = query

        if not telegram_chats:
            query = db_session.query(User.telegram_id)

        if (self.has_mailing == 'subscribed'
                and not telegram_chats):
            telegram_chats = query.filter(User.has_mailing.is_(True))

        if (self.has_mailing == 'unsubscribed'
                and not telegram_chats):
            telegram_chats = query.filter(User.has_mailing.is_(False))

        if (self.has_mailing == 'all'
                and not telegram_chats):
            telegram_chats = query

        chats = [user for user in telegram_chats]

        for i, part in enumerate(self.__split_chats(chats, config.NUMBER_USERS_TO_SEND)):
            context = {'message': message, 'chats': part}

            updater.job_queue.run_once(self.__send_by_subscription_status, i, context=context,
                                       name=f'Notification: {message[0:10]}_{i}')

        return True

    def __send_by_subscription_status(self, context):
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
                bot.send_message(chat_id=user.telegram_id, text=message, parse_mode=ParseMode.MARKDOWN)
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
