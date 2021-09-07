from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton,
                      ParseMode)
from telegram.ext import (CallbackContext,
                          ConversationHandler,
                          CallbackQueryHandler,)

from telegram import InlineKeyboardButton
from bot import common_comands
from bot.constants import constants
from bot.constants import command_constants
from bot.constants import states
from bot.decorators.logger import log_command
from bot.user_db import UserDB

user_db = UserDB()


@log_command(command=constants.LOG_COMMANDS_NAME['start_task_subscription'])
def start_task_subscription(update: Update, context: CallbackContext):
    context.user_data[states.SUBSCRIPTION_FLAG] = user_db.change_subscription(update.effective_user.id)
    user_categories = [
        category['name'] for category in user_db.get_categories(update.effective_user.id)
        if category['user_selected']
    ]
    answer = f'Отлично! Теперь я буду присылать тебе уведомления о ' \
                 f'новых заданиях в ' \
                 f'категориях: *{", ".join(user_categories)}*.\n\n' \
                 f'А пока можешь посмотреть открытые задания.'

    update.callback_query.edit_message_text(text=answer, parse_mode=ParseMode.MARKDOWN,
                                                reply_markup=common_comands.get_menu_and_tasks_buttons())
    update.callback_query.answer()
    return states.MENU


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
    update.callback_query.answer()
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
    update.callback_query.answer()
    return states.MENU


subscription_conv = ConversationHandler(
    allow_reentry=True,
    persistent=True,
    name='subscription_handler',
    entry_points=[
         CallbackQueryHandler(start_task_subscription, pattern=command_constants.COMMAND__START_SUBSCRIPTION),
         CallbackQueryHandler(stop_task_subscription, pattern=command_constants.COMMAND__STOP_SUBSCRIPTION),       
    ],
    states={
        states.CANCEL_FEEDBACK: [
                CallbackQueryHandler(cancel_feedback, pattern=command_constants.CANCEL_FEEDBACK__MANY_NOTIFICATION),
                CallbackQueryHandler(cancel_feedback, pattern=command_constants.CANCEL_FEEDBACK__NO_TIME),
                CallbackQueryHandler(cancel_feedback, pattern=command_constants.CANCEL_FEEDBACK__NO_RELEVANT_TASK),
                CallbackQueryHandler(cancel_feedback, pattern=command_constants.CANCEL_FEEDBACK__BOT_IS_BAD),
                CallbackQueryHandler(cancel_feedback, pattern=command_constants.CANCEL_FEEDBACK__FOND_IGNORE),
                CallbackQueryHandler(cancel_feedback, pattern=command_constants.CANCEL_FEEDBACK__ANOTHER)
            ],
    },
    fallbacks=[
        common_comands.start_command_handler,
        common_comands.menu_command_handler
    ],
    map_to_parent={
        states.MENU: states.MENU
    }
)
