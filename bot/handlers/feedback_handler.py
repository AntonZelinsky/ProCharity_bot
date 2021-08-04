from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram.ext import (CommandHandler,
                          ConversationHandler,
                          CallbackContext,
                          CallbackQueryHandler,
                          MessageHandler,
                          Filters)
from bot import common_comands
from bot.constants import states
from bot.constants import command_constants
from bot.constants import constants
from bot import email_client 
from bot.logger import log_command
from bot.user_db import UserDB

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

user_db = UserDB()


@log_command(command=constants.LOG_COMMANDS_NAME['ask_new_category'])
def ask_new_category(update: Update, context: CallbackContext):
    button = [
        [InlineKeyboardButton(text='Вернуться в меню', callback_data=command_constants.OPEN_MENU)]
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

    return states.TYPING


@log_command(command=constants.LOG_COMMANDS_NAME['ask_question'])
def ask_question(update: Update, context: CallbackContext):
    button = [
        [InlineKeyboardButton(text='Вернуться в меню', callback_data=command_constants.OPEN_MENU)]
    ]
    keyboard = InlineKeyboardMarkup(button)
    message = update.callback_query.edit_message_text(
        text='Напишите свой вопрос', reply_markup=keyboard
    )
    user_data = context.user_data
    user_data[MSG_ID] = message.message_id
    user_data[MSG_TEXT] = message.text
    user_data[FEEDBACK_TYPE] = QUESTION_TYPE

    return states.TYPING


@log_command(command=constants.LOG_COMMANDS_NAME['add_new_feature'])
def add_new_feature(update: Update, context: CallbackContext):
    button = [
        [InlineKeyboardButton(text='Вернуться в меню', callback_data=command_constants.OPEN_MENU)]
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

    return states.TYPING


# @log_command(command=constants.LOG_COMMANDS_NAME['save_user_input'])
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
        [InlineKeyboardButton(text='Не жду ответ', callback_data=command_constants.NO_WAIT)],
        [InlineKeyboardButton(text='Вернуться в меню', callback_data=command_constants.OPEN_MENU)]
    ]
    message = context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    context.user_data[ASK_EMAIL_MESSAGE_ID] = message.message_id
    context.user_data[ASK_EMAIL_MESSAGE_TEXT] = message.text

    return states.ASK_EMAIL


@log_command(command=constants.LOG_COMMANDS_NAME['no_wait_answer'])
def no_wait_answer(update: Update, context: CallbackContext):
    email_client.send_email(
        update.effective_user.id, context.user_data.get(USER_MSG),
        context.user_data.get(FEEDBACK_TYPE)
    )
    keyboard = common_comands.get_full_menu_buttons(context)
    text = 'Спасибо, я передал информацию команде ProCharity!'
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return states.MENU


# @log_command(command=LOG_COMMANDS_NAME['save_email'])
def save_email(update: Update, context: CallbackContext):
    user_input_email = update.message.text
    email_status = user_db.set_user_email(update.effective_user.id, user_input_email)
    if email_status:
        return after_get_feedback(update, context)
    else:
        return save_user_input(update, context)


@log_command(command=constants.LOG_COMMANDS_NAME['after_get_feedback'])
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
        text=text,
        reply_markup=keyboard
    )
    return states.MENU


feedback_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(ask_new_category, pattern=command_constants.ASK_NEW_CATEGORY),
        CallbackQueryHandler(ask_question, pattern=command_constants.ASK_QUESTION),
        CallbackQueryHandler(add_new_feature, pattern=command_constants.NEW_FEATURE)
    ],
    states={
        states.TYPING: [
            MessageHandler(Filters.text & ~Filters.command, save_user_input),
            CallbackQueryHandler(common_comands.open_menu, pattern=command_constants.OPEN_MENU)
        ],
        states.ASK_EMAIL: [
            CallbackQueryHandler(common_comands.open_menu, pattern=command_constants.OPEN_MENU),
            CallbackQueryHandler(no_wait_answer, pattern=command_constants.NO_WAIT),
            MessageHandler(Filters.text & ~Filters.command, save_email)
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
