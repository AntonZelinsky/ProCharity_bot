from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram.ext import (CallbackContext,
                          CommandHandler,
                          ConversationHandler,
                          CallbackQueryHandler,)

from telegram import InlineKeyboardButton
from bot import common_comands
from bot import constants
from bot import states
from bot import user_db
from bot.logger import log_command
from bot.user_db import UserDB

user_db = UserDB()


@log_command(command=constants.LOG_COMMANDS_NAME['stop_task_subscription'])
def stop_task_subscription(update: Update, context: CallbackContext):
    context.user_data[states.SUBSCRIPTION_FLAG] = user_db.change_subscription(update.effective_user.id)
    cancel_feedback_buttons = [
        [
            InlineKeyboardButton(text=reason[1], callback_data=reason[0])
        ] for reason in constants.REASONS.items()
    ]

    cancel_feedback_keyboard = InlineKeyboardMarkup(cancel_feedback_buttons)

    answer = ('Ты больше не будешь получать новые задания от фондов, но '
              'всегда сможешь найти их на сайте https://procharity.ru\n\n'
              'Поделись, пожалуйста, почему ты решил отписаться?')

    update.callback_query.edit_message_text(
        text=answer, reply_markup=cancel_feedback_keyboard, disable_web_page_preview=True
    )

    return states.CANCEL_FEEDBACK


@log_command(command=constants.LOG_COMMANDS_NAME['cancel_feedback'])
def cancel_feedback(update: Update, context: CallbackContext):
    keyboard = common_comands.get_full_menu_buttons(context)
    reason_canceling = update['callback_query']['data']
    telegram_id = update['callback_query']['message']['chat']['id']
    user_db.cancel_feedback_stat(telegram_id, reason_canceling)
    
    update.callback_query.edit_message_text(
        text='Спасибо, я передал информацию команде ProCharity!',
        reply_markup=keyboard
    )
    return states.MENU


stop_subscription_conv = ConversationHandler(
    entry_points=[
         CallbackQueryHandler(stop_task_subscription, pattern='^stop_subscription$'),
    ],
    states={
      
       states.CANCEL_FEEDBACK: [
                CallbackQueryHandler(cancel_feedback, pattern='^many_notification$'),
                CallbackQueryHandler(cancel_feedback, pattern='^no_time$'),
                CallbackQueryHandler(cancel_feedback, pattern='^no_relevant_task$'),
                CallbackQueryHandler(cancel_feedback, pattern='^bot_is_bad$'),
                CallbackQueryHandler(cancel_feedback, pattern='^fond_ignore'),
                CallbackQueryHandler(cancel_feedback, pattern='^another')
            ]
    },
    fallbacks=[
        CommandHandler('start', common_comands.start),
        CommandHandler('menu', common_comands.open_menu_fall)
    ],
    map_to_parent={
        states.MENU: states.MENU
    }
)
