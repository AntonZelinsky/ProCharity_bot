from telegram import (Update,
                      InlineKeyboardMarkup,
                      ParseMode)
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler
from telegram import InlineKeyboardButton

from app import config
from bot.constants import states
from bot.constants import command_constants
from bot.constants import constants
from bot.decorators.actions import send_typing_action
from bot.decorators.logger import log_command
from core.repositories.user_repository import UserRepository
from core.services.user_service import UserService
from app.database import db_session


MENU_BUTTONS = [
    [
        InlineKeyboardButton(
            text='🔎 Посмотреть открытые задания', callback_data=command_constants.COMMAND__OPEN_TASK
        )
    ],
    [
        InlineKeyboardButton(
            text='✏️ Изменить компетенции', callback_data=command_constants.COMMAND__CHANGE_CATEGORY
        )
    ],
    [
        InlineKeyboardButton(
            text='✉️ Отправить предложение/ошибку', callback_data=command_constants.COMMAND__NEW_FEATURE
        )
    ],
    [
        InlineKeyboardButton(
            text='❓ Задать вопрос', callback_data=command_constants.COMMAND__ASK_QUESTION
        )
    ],
    [
        InlineKeyboardButton(
            text='ℹ️ О платформе', callback_data=command_constants.COMMAND__ABOUT
        )
    ],
    [
        InlineKeyboardButton(
            text='⏹ Остановить/включить подписку на задания',
            callback_data=command_constants.COMMAND__STOP_SUBSCRIPTION
        )
    ]
]

user_repository = UserRepository(db_session)
user_db = UserService(user_repository)


@send_typing_action
@log_command(command=constants.LOG_COMMANDS_NAME['start'])
def start(update: Update, context: CallbackContext) -> int:
    deeplink_passed_param = context.args
    user = user_db.add_user(update.effective_user, deeplink_passed_param)
    context.user_data[states.SUBSCRIPTION_FLAG] = user.has_mailing

    callback_data = (command_constants.COMMAND__GREETING_REGISTERED_USER
                     if user.categories
                     else command_constants.COMMAND__GREETING)
    buttons = [
        [InlineKeyboardButton(text='Начнем', callback_data=callback_data)],
        [InlineKeyboardButton(
            text='Связать аккаунт с ботом',
            url=f'{config.URL_PROCHARITY}/auth/bot_procharity.php?user_id={user.external_id}&telegram_id={user.telegram_id}'
        )]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Привет! 👋 \n\n'
             f'Я бот платформы интеллектуального волонтерства <a href="https://procharity.ru/">ProCharity</a>. '
             'Буду держать тебя в курсе новых задач и помогу '
             'оперативно связаться с командой поддержки.'
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )
    return states.GREETING


@log_command(command=constants.LOG_COMMANDS_NAME['open_menu'])
def open_menu(update: Update, context: CallbackContext):
    keyboard = get_full_menu_buttons(context)
    text = 'Меню'
    if update.callback_query is not None:
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
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
            callback_data=command_constants.COMMAND__STOP_SUBSCRIPTION
        )
    elif not context.user_data.get(states.CATEGORIES_SELECTED):
        return InlineKeyboardButton(
        text='▶️ Включить подписку на задания',
        callback_data=command_constants.COMMAND__CHANGE_CATEGORY
    )
    else:
        return InlineKeyboardButton(
        text='▶️ Включить подписку на задания',
        callback_data=command_constants.COMMAND__START_SUBSCRIPTION
    )


def get_menu_and_tasks_buttons():
    buttons = [
        [
            InlineKeyboardButton(text='Посмотреть открытые задания', callback_data=command_constants.COMMAND__OPEN_TASK)
        ],
        [
            InlineKeyboardButton(text='Открыть меню', callback_data=command_constants.COMMAND__OPEN_MENU)
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    return keyboard

open_menu_button = InlineKeyboardButton(text='Открыть меню', callback_data=command_constants.COMMAND__OPEN_MENU)

open_menu_handler = CallbackQueryHandler(open_menu, pattern=command_constants.COMMAND__OPEN_MENU)

start_command_handler = CommandHandler('start', start)
menu_command_handler = CommandHandler('menu', open_menu)
