from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram.ext import CallbackContext

from telegram import InlineKeyboardButton
from bot import states
from bot.logger import log_command
from bot.constants import BOT_NAME, LOG_COMMANDS_NAME
from bot.user_db import UserDB

MENU_BUTTONS = [
    [
        InlineKeyboardButton(
            text='🔎 Посмотреть открытые задания', callback_data='open_task'
        )
    ],
    [
        InlineKeyboardButton(
            text='✏️ Изменить компетенции', callback_data='change_category'
        )
    ],
    [
        InlineKeyboardButton(
            text='✉️ Отправить предложение/ошибку', callback_data='new_feature'
        )
    ],
    [
        InlineKeyboardButton(
            text='❓ Задать вопрос', callback_data='ask_question'
        )
    ],
    [
        InlineKeyboardButton(
            text='ℹ️ О платформе', callback_data='about'
        )
    ],
    [
        InlineKeyboardButton(
            text='⏹ Остановить/включить подписку на задания',
            callback_data='stop_subscription'
        )
    ]
]

user_db = UserDB()


@log_command(command=LOG_COMMANDS_NAME['start'])
def start(update: Update, context: CallbackContext) -> int:
    deeplink_passed_param = context.args
    user = user_db.add_user(update.effective_user, deeplink_passed_param)
    context.user_data[states.SUBSCRIPTION_FLAG] = user.has_mailing

    callback_data = (states.GREETING_REGISTERED_USER
                     if user.categories
                     else states.GREETING)
    button = [
        [
            InlineKeyboardButton(text='Начнем', callback_data=callback_data)
        ]
    ]
    keyboard = InlineKeyboardMarkup(button)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Привет! 👋 \n\n'
             f'Меня зовут {BOT_NAME}. '
             'Буду держать тебя в курсе новых задач и помогу '
             'оперативно связаться с командой поддержки.',
        reply_markup=keyboard
    )
    return states.GREETING


@log_command(command=LOG_COMMANDS_NAME['open_menu'])
def open_menu(update: Update, context: CallbackContext):
    subscription_button = get_subscription_button(context)
    MENU_BUTTONS[-1] = [subscription_button]
    keyboard = InlineKeyboardMarkup(MENU_BUTTONS)
    text = 'Меню'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return states.MENU


def open_menu_fall(update: Update, context: CallbackContext):
    subscription_button = get_subscription_button(context)
    MENU_BUTTONS[-1] = [subscription_button]
    keyboard = InlineKeyboardMarkup(MENU_BUTTONS)
    text = 'Меню'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=keyboard
    )
    return states.MENU


def get_subscription_button(context: CallbackContext):
    if context.user_data[states.SUBSCRIPTION_FLAG]:
        return InlineKeyboardButton(
            text='⏹ Остановить подписку на задания',
            callback_data='stop_subscription'
        )
    return InlineKeyboardButton(
        text='▶️ Включить подписку на задания',
        callback_data='start_subscription'
    )