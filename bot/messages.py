import time
from dataclasses import dataclass
from typing import List

from telegram import Bot, ParseMode, error
from telegram.error import Unauthorized

from app import config
from app.database import db_session
from app.error_handlers import InvalidAPIUsage
from app.logger import bot_logger as logger
from app.models import User
from bot.charity_bot import dispatcher

bot = Bot(config.TELEGRAM_TOKEN)


@dataclass
class SendUserMessageContext:
    message: str
    telegram_id: int


@dataclass
class SendUserNotificationsContext:
    user_message_context: List[SendUserMessageContext]


class TelegramNotification:
    """
    This class describes the functionality
    for working with notifications in Telegram.
    """

    def __init__(self, mode: str = 'subscribed') -> None:
        self.mode = mode

    # TODO refactoring https://github.com/python-telegram-bot/python-telegram-bot/wiki/Avoiding-flood-limits
    def send_notification(self, message):
        """
           Adds queue to send notification to telegram chats.

        :param message: Message to add to the sending queue
        :param telegram_chats: Users query
        :return:
        """
        if self.mode not in ('all', 'subscribed', 'unsubscribed'):
            return False

        chats_list = []
        query = db_session.query(User.telegram_id).filter(User.banned.is_(False))

        if self.mode == 'subscribed':
            chats_list = query.filter(User.has_mailing.is_(True))

        if self.mode == 'unsubscribed':
            chats_list = query.filter(User.has_mailing.is_(False))

        if self.mode == 'all':
            chats_list = query

        user_notification_context = SendUserNotificationsContext([])
        for user in chats_list:
            user_message_context = SendUserMessageContext(
                message=message,
                telegram_id=user.telegram_id
            )
            user_notification_context.user_message_context.append(
                user_message_context
            )

        seconds = 1

        dispatcher.job_queue.run_once(
            self.send_batch_messages,
            seconds,
            context=user_notification_context,
            name=f'Sending: {message[0:10]}'
        )

        return True

    def send_batch_messages(self, user_notification_context):
        job = user_notification_context.job
        user_message_context = job.context.user_message_context
        for send_set in self.__split_chats(
            user_message_context,
            config.MAILING_BATCH_SIZE
        ):
            for user_message_context in send_set:
                self.__send_message_context(user_message_context)
            time.sleep(1)

    def __send_message_context(self, user_message_context):
        tries = 3
        for i in range(tries):
            try:
                bot.send_message(
                    chat_id=user_message_context.telegram_id,
                    text=user_message_context.message,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )
                logger.info(
                    f"Sent message to {user_message_context.telegram_id}"
                )
                return
            except error.BadRequest as ex:
                logger.error(
                    f'{str(ex.message)}, telegram_id: '
                    f'{user_message_context.telegram_id}')
                if i < tries:
                    logger.info(f"Retry to send after {i}")
                    time.sleep(i)
            except Unauthorized as ex:
                logger.error(
                    f'{str(ex.message)}: {user_message_context.telegram_id}'
                    )
                User.query.filter_by(
                    telegram_id=user_message_context.telegram_id
                    ).update({'banned': True, 'has_mailing': False})
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


class TelegramMessage:
    """
    This class describes the functionality for
    working with message to user in Telegram.
    """

    def __init__(self, telegram_id: int) -> None:
        self.telegram_id = telegram_id

    def send_message(self, message) -> None:
        """
           Send telegram message to user.

        :param message: Message to send
        :return:
        """

        if not db_session.query(
            User
        ).filter(User.telegram_id == self.telegram_id):
            logger.error(
                f'User with telegram id "{self.telegram_id}" does not exist'
            )
            raise InvalidAPIUsage(f'Пользователь с таким telegram id '
                                  f'"{self.telegram_id}" не существует'
                                  )

        try:
            bot.send_message(
                chat_id=self.telegram_id, text=message,
                parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            logger.info(f'Sent message to {self.telegram_id}')

        except error.BadRequest as ex:
            logger.error(f'{str(ex.message)}, telegram_id: {self.telegram_id}')
            raise InvalidAPIUsage('Неверно указан параметр <telegram_id>. Сообщение не отправлено.')
        except Unauthorized as ex:
            logger.error(f'{str(ex.message)}: {self.telegram_id}')
            User.query.filter_by(
                telegram_id=self.telegram_id
                ).update({'banned': True, 'has_mailing': False})
            db_session.commit()
            raise InvalidAPIUsage(f'{str(ex.message)}: {self.telegram_id}')
