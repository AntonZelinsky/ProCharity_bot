import os
from functools import lru_cache
from queue import Queue
from threading import Thread

from dotenv import load_dotenv
from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton,
                      ParseMode)
from telegram.ext import (Updater,
                          ConversationHandler,
                          CallbackContext,
                          CallbackQueryHandler,
                          PicklePersistence, Dispatcher, JobQueue, ExtBot)
from telegram.utils.request import Request

from app.config import BOT_PERSISTENCE_FILE, HOST_NAME, WEBHOOK_URL, USE_WEBHOOK
from app.logger import bot_logger
from bot import common_comands
from bot.constants import command_constants
from bot.constants import constants
from bot.constants import states
from bot.decorators.logger import log_command
from bot.handlers.categories_handler import categories_conv, change_user_categories
from bot.handlers.feedback_handler import feedback_conv
from bot.handlers.subscription_handler import subscription_conv
from bot.user_db import UserDB

load_dotenv()

logger = bot_logger

user_db = UserDB()


@log_command(command=constants.LOG_COMMANDS_NAME['about'])
def about(update: Update, context: CallbackContext):
    button = [
        [InlineKeyboardButton(text='Вернуться в меню', callback_data=command_constants.COMMAND__OPEN_MENU)]
    ]
    keyboard = InlineKeyboardMarkup(button)
    update.callback_query.edit_message_text(
        text='С ProCharity профессионалы могут помочь некоммерческим '
             'организациям в вопросах, которые требуют специальных знаний и '
             'опыта.\n\nИнтеллектуальный волонтёр безвозмездно дарит фонду своё '
             'время и профессиональные навыки, позволяя решать задачи, '
             'которые трудно закрыть силами штатных сотрудников.\n\n'
             'Сделано студентами <a href="https://praktikum.yandex.ru/">Яндекс.Практикума.</a>',
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )
    update.callback_query.answer()
    return states.MENU


def error_handler(update: Update, context: CallbackContext) -> None:
    if update is not None and update.effective_user is not None:
        text = f"Error '{context.error}', user id: {update.effective_user.id}"
        message = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Что-то пошло не так, сообщите пожалуйста об этом администрации."
        )
    else:
        text = f"Error '{context.error}'"
    logger.error(msg=text, exc_info=context.error)


def init_pooling(bot, persistence):
    updater = Updater(bot=bot, persistence=persistence)
    updater.start_polling()

    logger.info('Bot started through pulling')
    return updater.dispatcher


def init_webhook(bot, persistence, webhook_url):
    update_queue = Queue()
    job_queue = JobQueue()
    dispatcher = Dispatcher(bot, update_queue, persistence=persistence)
    job_queue.set_dispatcher(dispatcher)
    success_setup = bot.set_webhook(webhook_url)
    if not success_setup:
        print(webhook_url)
        raise AttributeError("Cannot set up telegram webhook")
    thread = Thread(target=dispatcher.start, name='dispatcher')
    thread.start()

    logger.info('Bot started through webhooks')
    return dispatcher


@lru_cache(maxsize=None)
def init() -> Dispatcher:
    token = os.getenv('TOKEN')
    request = Request(con_pool_size=8)
    bot = ExtBot(token, request=request)
    bot_persistence = PicklePersistence(filename=BOT_PERSISTENCE_FILE,
                                        store_bot_data=True,
                                        store_user_data=True,
                                        store_callback_data=True,
                                        store_chat_data=True)

    if HOST_NAME and USE_WEBHOOK:
        dispatcher = init_webhook(bot, bot_persistence, WEBHOOK_URL)
    else:
        dispatcher = init_pooling(bot, bot_persistence)

    conv_handler = ConversationHandler(
        entry_points=[
            common_comands.start_command_handler
        ],
        states={
            states.GREETING: [
                categories_conv,
            ],
            states.MENU: [
                feedback_conv,
                categories_conv,
                subscription_conv,
                CallbackQueryHandler(about, pattern=command_constants.COMMAND__ABOUT),
                common_comands.open_menu_handler
            ],
        },
        fallbacks=[
            common_comands.start_command_handler,
            common_comands.menu_command_handler
        ],
        persistent=True,
        name='main_handler'
    )

    update_users_category = CallbackQueryHandler(change_user_categories, pattern='^up_cat[0-9]{1,2}$')

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(update_users_category)
    dispatcher.add_error_handler(error_handler)

    return dispatcher


dispatcher = init()
