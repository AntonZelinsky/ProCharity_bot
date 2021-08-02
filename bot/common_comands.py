from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton,
                      ReplyKeyboardMarkup,
                      KeyboardButton)
from telegram.ext import CallbackContext

from telegram import InlineKeyboardButton
from bot import states
from bot.logger import log_command
from bot.constants import BOT_NAME, LOG_COMMANDS_NAME
from bot.user_db import UserDB

MENU_BUTTONS = [
    [
        KeyboardButton(
            text='🔎 Посмотреть открытые задания'
        )
    ],
    [
        KeyboardButton(
            text='✏️ Изменить компетенции'
        )
    ],
    [
        KeyboardButton(
            text='✉️ Отправить предложение/ошибку')
    ],
    [
        KeyboardButton(
            text='❓ Задать вопрос'
        )
    ],
    [
        KeyboardButton(
            text='ℹ️ О платформе'
        )
    ],
    [
        KeyboardButton(
            text='⏹ Остановить/включить подписку на задания'
        )
    ]
]

user_db = UserDB()


@log_command(command=LOG_COMMANDS_NAME['start'])
def start(update: Update, context: CallbackContext) -> int:
    deeplink_passed_param = context.args
    user = user_db.add_user(update.effective_user, deeplink_passed_param)
    context.user_data[states.SUBSCRIPTION_FLAG] = user.has_mailing  
    reply_keyboard = [['Начнем']]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Привет! 👋 \n\n'
             f'Меня зовут {BOT_NAME}. '
             'Буду держать тебя в курсе новых задач и помогу '
             'оперативно связаться с командой поддержки.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True,
        ),
    )
    
    return states.GREETING_REGISTERED_USER if user.categories else states.GREETING


@log_command(command=LOG_COMMANDS_NAME['open_menu'])
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
    keyboard = ReplyKeyboardMarkup(MENU_BUTTONS, resize_keyboard=True, one_time_keyboard=True)
    return keyboard


def get_subscription_button(context: CallbackContext):
    if context.user_data[states.SUBSCRIPTION_FLAG]:
        return KeyboardButton(
            text='⏹ Остановить подписку на задания'
        )
    return KeyboardButton(
        text='▶️ Включить подписку на задания'
    )


def get_menu_and_tasks_buttons():
    buttons = [
        [
            KeyboardButton(text='Посмотреть открытые задания', callback_data='open_task')
        ],
        [
            KeyboardButton(text='Открыть меню', callback_data='open_menu')
        ]
    ]
    keyboard = ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=True)
    return keyboard