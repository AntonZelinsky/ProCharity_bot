import os
import re

from dotenv import load_dotenv
from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton,
                      ParseMode)
from telegram.ext import (Updater,
                          ConversationHandler,
                          CallbackContext,
                          CallbackQueryHandler,
                          PicklePersistence)

from app.config import BOT_PERSISTENCE_FILE, HOST_NAME

from bot import common_comands
from bot.constants import states
from bot.constants import constants
from bot.constants import command_constants
from bot.handlers.categories_handler import categories_conv, change_user_categories
from bot.handlers.feedback_handler import feedback_conv
from bot.handlers.subscription_handler import subscription_conv
from bot.decorators.logger import log_command
from bot.user_db import UserDB
from app.logger import bot_logger

load_dotenv()

logger = bot_logger

bot_persistence = PicklePersistence(filename=BOT_PERSISTENCE_FILE,
                                    store_bot_data=True,
                                    store_user_data=True,
                                    store_callback_data=True,
                                    store_chat_data=True)

updater = Updater(token=os.getenv('TOKEN'), persistence=bot_persistence, use_context=True)

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
    else:
        text = f"Error '{context.error}'"
    logger.error(msg=text, exc_info=context.error)


def init() -> None:
    dispatcher = updater.dispatcher
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
    if re.search(r'localhost', HOST_NAME):
        updater.start_polling()
    else:
        updater.start_webhook(
        listen='127.0.0.1',
        port=5000,
        url_path=os.getenv('TOKEN'),
        webhook_url=f"{HOST_NAME}/{os.getenv('TOKEN')}",
        #cert='cert.pem'
        )
