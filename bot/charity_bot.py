import logging
import os

from dotenv import load_dotenv
from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram.ext import (Updater,
                          CommandHandler,
                          ConversationHandler,
                          CallbackContext,
                          CallbackQueryHandler,
                          PicklePersistence)

from app.config import BOT_PERSISTENCE_FILE

from bot import states
from bot import common_comands
from bot import constants

from bot.handlers.categories_handler import categories_conv, change_user_categories
from bot.handlers.feedback_handler import feedback_conv
from bot.handlers.subscription_handler import subscription_conv
from bot.logger import log_command
from bot.user_db import UserDB


load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

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
        [InlineKeyboardButton(text='Вернуться в меню', callback_data='open_menu')]
    ]
    keyboard = InlineKeyboardMarkup(button)
    update.callback_query.edit_message_text(
        text='С ProCharity профессионалы могут помочь некоммерческим '
             'организациям в вопросах, которые требуют специальных знаний и '
             'опыта.\n\nИнтеллектуальный волонтёр безвозмездно дарит фонду своё '
             'время и профессиональные навыки, позволяя решать задачи, '
             'которые трудно закрыть силами штатных сотрудников.',
        reply_markup=keyboard
    )

    return states.MENU


def error_handler(update: Update, context: CallbackContext) -> None:
    if update.effective_user is not None:
        text = f"Error '{context.error}', user id: {update.effective_user.id}"
    else:
        text = f"Error '{context.error}'"
    logger.error(msg=text, exc_info=context.error)


def init() -> None:
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', common_comands.start)
        ],
        states={
            states.GREETING: [
               categories_conv,
            ],  
            states.MENU: [
                feedback_conv,
                categories_conv,
                subscription_conv,
                CallbackQueryHandler(about, pattern='^about$'),                
                CallbackQueryHandler(common_comands.open_menu, pattern='^open_menu$')
            ],            
        },
        fallbacks=[
            CommandHandler('start', common_comands.start),
            CommandHandler('menu', common_comands.open_menu_fall)
        ],
        persistent=True,
        name='conv_handler'
    )

    update_users_category = CallbackQueryHandler(change_user_categories, pattern='^up_cat[0-9]{1,2}$')

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(update_users_category)
    dispatcher.add_error_handler(error_handler)
    updater.start_polling()
