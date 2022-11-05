from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram.ext import (ConversationHandler,
                          CallbackContext,
                          CallbackQueryHandler,
                          MessageHandler,
                          Filters)

from app.database import db_session
from bot import common_comands
from bot.constants import states
from bot.constants import command_constants
from bot.constants import constants
from bot import email_client
from bot.decorators.actions import send_typing_action
from bot.decorators.logger import log_command
from core.repositories.user_repository import UserRepository
from core.services.user_service import UserService


ASK_EMAIL_FLAG = 'ask_email_flag'
ASK_EMAIL_MESSAGE_ID = 'ask_email_message_id'
ASK_EMAIL_MESSAGE_TEXT = 'ask_email_message_text'
USER_MSG = 'user_msg'
FEEDBACK_TYPE = 'feedback_type'
QUESTION_TYPE = 'question'
CATEGORY_TYPE = 'category'
FEATURE_TYPE = 'feature'
MSG_ID = 'msg_id'
MSG_TEXT = 'msg_text'

user_repository = UserRepository(db_session)
user_db = UserService(user_repository)


@log_command(command=constants.LOG_COMMANDS_NAME['ask_new_category'])
def ask_new_category(update: Update, context: CallbackContext):
    button = [
        [InlineKeyboardButton(text='Вернуться в меню', callback_data=command_constants.COMMAND__OPEN_MENU)]
    ]
    keyboard = InlineKeyboardMarkup(button)
    message = update.callback_query.edit_message_text(
        text='Напиши, в какой профессиональной сфере ты бы хотел помогать?',
        reply_markup=keyboard
    )
    user_data = context.user_data
    user_data[MSG_ID] = message.message_id
    user_data[MSG_TEXT] = message.text
    user_data[FEEDBACK_TYPE] = CATEGORY_TYPE
    update.callback_query.answer()
    return states.TYPING


@log_command(command=constants.LOG_COMMANDS_NAME['ask_question'])
def ask_question(update: Update, context: CallbackContext):
    button = [
        [InlineKeyboardButton(text='Вернуться в меню', callback_data=command_constants.COMMAND__OPEN_MENU)]
    ]
    keyboard = InlineKeyboardMarkup(button)
    message = update.callback_query.edit_message_text(
        text='Напишите свой вопрос', reply_markup=keyboard
    )
    user_data = context.user_data
    user_data[MSG_ID] = message.message_id
    user_data[MSG_TEXT] = message.text
    user_data[FEEDBACK_TYPE] = QUESTION_TYPE
    update.callback_query.answer()
    return states.TYPING


@log_command(command=constants.LOG_COMMANDS_NAME['add_new_feature'])
def add_new_feature(update: Update, context: CallbackContext):
    button = [
        [InlineKeyboardButton(text='Вернуться в меню', callback_data=command_constants.COMMAND__OPEN_MENU)]
    ]
    keyboard = InlineKeyboardMarkup(button)
    message = update.callback_query.edit_message_text(
        text='Расскажи, какого функционала тебе не хватает?',
        reply_markup=keyboard
    )
    user_data = context.user_data
    user_data[MSG_ID] = message.message_id
    user_data[MSG_TEXT] = message.text
    user_data[FEEDBACK_TYPE] = FEATURE_TYPE
    update.callback_query.answer()
    return states.TYPING


@send_typing_action
@log_command(command=constants.LOG_COMMANDS_NAME['save_user_input'])
def save_user_input(update: Update, context: CallbackContext):
    user = user_db.get_user(update.effective_user.id)
    context.user_data[USER_MSG] = update.message.text
    if user.email:
        return after_get_feedback(update, context)
    else:
        return ask_email(update, context)


@log_command(command=constants.LOG_COMMANDS_NAME['ask_email'])
def ask_email(update: Update, context: CallbackContext):
    context.user_data[ASK_EMAIL_FLAG] = True
    context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=context.user_data.get(MSG_ID),
        text=context.user_data.get(MSG_TEXT)
    )
    del context.user_data[MSG_ID]

    text = 'Пожалуйста, укажи свою почту, если хочешь получить ответ'
    buttons = [
        [InlineKeyboardButton(text='Не жду ответ', callback_data=command_constants.COMMAND__NO_WAIT)],
        [InlineKeyboardButton(text='Вернуться в меню', callback_data=command_constants.COMMAND__OPEN_MENU)]
    ]
    message = context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    context.user_data[ASK_EMAIL_MESSAGE_ID] = message.message_id
    context.user_data[ASK_EMAIL_MESSAGE_TEXT] = message.text
    update.callback_query.answer()
    return states.ASK_EMAIL


@send_typing_action
@log_command(command=constants.LOG_COMMANDS_NAME['no_wait_answer'])
def no_wait_answer(update: Update, context: CallbackContext):
    email_client.send_email(
        update.effective_user.id, context.user_data.get(USER_MSG),
        context.user_data.get(FEEDBACK_TYPE)
    )
    keyboard = common_comands.get_full_menu_buttons(context)
    text = 'Спасибо, я передал информацию команде ProCharity!'
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    update.callback_query.answer()
    return states.MENU


@send_typing_action
@log_command(command=constants.LOG_COMMANDS_NAME['email_feedback'])
def save_email(update: Update, context: CallbackContext):
    user_input_email = update.message.text
    email_status = user_db.set_user_email(update.effective_user.id, user_input_email)
    if email_status:
        return after_get_feedback(update, context)
    else:
        return save_user_input(update, context)


def after_get_feedback(update: Update, context: CallbackContext):
    if context.user_data.get(ASK_EMAIL_FLAG):
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.user_data[ASK_EMAIL_MESSAGE_ID],
            text=context.user_data.get(ASK_EMAIL_MESSAGE_TEXT)
        )
        del context.user_data[ASK_EMAIL_FLAG]
        del context.user_data[ASK_EMAIL_MESSAGE_ID]
        del context.user_data[ASK_EMAIL_MESSAGE_TEXT]

    if context.user_data.get(MSG_ID):
        context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=context.user_data.get(MSG_ID),
            text=context.user_data.get(MSG_TEXT)
        )
        del context.user_data[MSG_ID]
        del context.user_data[MSG_TEXT]

    user = user_db.get_user(update.effective_user.id)

    feedback_type = context.user_data.get(FEEDBACK_TYPE)

    email_client.send_email(
        update.effective_user.id, context.user_data.get(USER_MSG), feedback_type
    )
    del context.user_data[FEEDBACK_TYPE]

    keyboard = common_comands.get_full_menu_buttons(context)
    text = f'Спасибо, я передал информацию команде ProCharity! Ответ придет на почту {user.email}'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text
    )
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Меню',
        reply_markup=keyboard
    )
    update.callback_query.answer()
    return states.MENU


feedback_conv = ConversationHandler(
    allow_reentry=True,
    persistent=True,
    name='feedback_handler',
    entry_points=[
        CallbackQueryHandler(ask_new_category, pattern=command_constants.COMMAND__ASK_NEW_CATEGORY),
        CallbackQueryHandler(ask_question, pattern=command_constants.COMMAND__ASK_QUESTION),
        CallbackQueryHandler(add_new_feature, pattern=command_constants.COMMAND__NEW_FEATURE)
    ],
    states={
        states.TYPING: [
            MessageHandler(Filters.text & ~Filters.command, save_user_input),
            common_comands.open_menu_handler
        ],
        states.ASK_EMAIL: [
            common_comands.open_menu_handler,
            CallbackQueryHandler(no_wait_answer, pattern=command_constants.COMMAND__NO_WAIT),
            MessageHandler(Filters.text & ~Filters.command, save_email)
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
