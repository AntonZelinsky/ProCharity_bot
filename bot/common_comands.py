from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram.ext import CallbackContext

from telegram import InlineKeyboardButton
from bot.constants import states
from bot.constants import command_constants
from bot.constants import constants
from bot.logger import log_command
from bot.user_db import UserDB

MENU_BUTTONS = [
    [
        InlineKeyboardButton(
            text='🔎 Посмотреть открытые задания', callback_data=command_constants.OPEN_TASK
        )
    ],
    [
        InlineKeyboardButton(
            text='✏️ Изменить компетенции', callback_data=command_constants.CHANGE_CATEGORY
        )
    ],
    [
        InlineKeyboardButton(
            text='✉️ Отправить предложение/ошибку', callback_data=command_constants.NEW_FEATURE
        )
    ],
    [
        InlineKeyboardButton(
            text='❓ Задать вопрос', callback_data=command_constants.ASK_QUESTION
        )
    ],
    [
        InlineKeyboardButton(
            text='ℹ️ О платформе', callback_data=command_constants.ABOUT
        )
    ],
    [
        InlineKeyboardButton(
            text='⏹ Остановить/включить подписку на задания',
            callback_data=command_constants.STOP_SUBSCRIPTION
        )
    ]
]

user_db = UserDB()


@log_command(command=constants.LOG_COMMANDS_NAME['start'])
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
             f'Меня зовут {constants.BOT_NAME}. '
             'Буду держать тебя в курсе новых задач и помогу '
             'оперативно связаться с командой поддержки.',
        reply_markup=keyboard
    )
    return states.GREETING


@log_command(command=constants.LOG_COMMANDS_NAME['open_menu'])
def open_menu(update: Update, context: CallbackContext):
    keyboard = get_full_menu_buttons(context)
    text = 'Меню'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return states.MENU


def open_menu_fall(update: Update, context: CallbackContext):
    keyboard = get_full_menu_buttons(context)
    text = 'Меню'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=keyboard
    )
    return states.MENU


def get_full_menu_buttons(context: CallbackContext):
    subscription_button = get_subscription_button(context)
    MENU_BUTTONS[-1] = [subscription_button]
    keyboard = InlineKeyboardMarkup(MENU_BUTTONS)
    return keyboard


def get_subscription_button(context: CallbackContext):
    if context.user_data[states.SUBSCRIPTION_FLAG]:
        return InlineKeyboardButton(
            text='⏹ Остановить подписку на задания',
            callback_data=command_constants.STOP_SUBSCRIPTION
        )
    return InlineKeyboardButton(
        text='▶️ Включить подписку на задания',
        callback_data=command_constants.START_SUBSCRIPTION
    )


def get_menu_and_tasks_buttons():
    buttons = [
        [
            InlineKeyboardButton(text='Посмотреть открытые задания', callback_data=command_constants.OPEN_TASK)
        ],
        [
            InlineKeyboardButton(text='Открыть меню', callback_data=command_constants.OPEN_MENU)
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    return keyboard