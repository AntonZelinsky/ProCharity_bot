from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram.ext import CallbackContext

from telegram import InlineKeyboardButton
from bot import common_comands
from bot import constants
from bot import states
from bot import user_db
from bot.logger import log_command
from bot.user_db import UserDB

user_db = UserDB()


@log_command(command=constants.LOG_COMMANDS_NAME['start_task_subscription'])
def start_task_subscription(update: Update, context: CallbackContext):
    context.user_data[states.SUBSCRIPTION_FLAG] = user_db.change_subscription(update.effective_user.id)
    user_categories = [
        c['name'] for c in user_db.get_category(update.effective_user.id)
        if c['user_selected']
    ]

    answer = f'Отлично! Теперь я буду присылать тебе уведомления о ' \
             f'новых заданиях в ' \
             f'категориях: {", ".join(user_categories)}.\n\n' \
             f'А пока можешь посмотреть открытые задания.'

    update.callback_query.edit_message_text(text=answer,
                                            reply_markup=common_comands.get_menu_and_tasks_buttons())

    return states.AFTER_CATEGORY_REPLY


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
