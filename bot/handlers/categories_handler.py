import re

from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton,
                      ParseMode)
from telegram.ext import (CallbackContext,
                          ConversationHandler,
                          CallbackQueryHandler,
                          CommandHandler)

from telegram import InlineKeyboardButton

from bot import common_comands
from bot import formatter
from bot.constants import constants
from bot.constants import command_constants
from bot.constants import states
from bot import user_db
from bot.logger import log_command
from bot.user_db import UserDB
from bot.handlers.feedback_handler import feedback_conv

user_db = UserDB()

PAGINATION = 3


def choose_category_after_start(update: Update, context: CallbackContext):
    update.callback_query.edit_message_text(
        text=update.callback_query.message.text_html,
        parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )
    return choose_category(update, context, True)


def before_confirm_specializations(update: Update, context: CallbackContext):
    update.callback_query.edit_message_text(
        text=update.callback_query.message.text_html,
        parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )
    return confirm_specializations(update, context)


@log_command(command=constants.LOG_COMMANDS_NAME['confirm_specializations'])
def confirm_specializations(update: Update, context: CallbackContext):
    buttons = [
        [
            InlineKeyboardButton(text='Да', callback_data=command_constants.COMMAND__READY)
        ],
        [
            InlineKeyboardButton(text='Нет, хочу изменить.', callback_data=command_constants.COMMAND__RETURN_CHOSE_CATEGORY)
        ]
    ]
    specializations = ', '.join([spec['name'] for spec
                                 in user_db.get_category(update.effective_user.id)
                                 if spec['user_selected']])

    if not specializations:
        specializations = 'Категории ещё не выбраны'

    keyboard = InlineKeyboardMarkup(buttons)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Вот список твоих профессиональных компетенций:'
             f' *{specializations}*. Все верно?',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard,
    )
    return states.CATEGORY


@log_command(command=constants.LOG_COMMANDS_NAME['change_user_categories'])
def change_user_categories(update: Update, context: CallbackContext):
    """Auxiliary function for selecting a category and changing the status of subscriptions."""
    pattern_id = re.findall(r'\d+', update.callback_query.data)
    category_id = int(pattern_id[0])
    telegram_id = update.effective_user.id

    user_db.change_user_category(telegram_id=telegram_id, category_id=category_id)
    choose_category(update, context)
    update.callback_query.answer()


@log_command(command=constants.LOG_COMMANDS_NAME['choose_category'],
             ignore_func=['change_user_categories'])
def choose_category(update: Update, context: CallbackContext, save_prev_msg: bool = False):
    """The main function is to select categories for subscribing to them."""
    categories = user_db.get_category(update.effective_user.id)

    buttons = []
    for cat in categories:
        if cat['user_selected']:
            cat['name'] += " ✅"
        buttons.append([InlineKeyboardButton(text=cat['name'], callback_data=f'up_cat{cat["category_id"]}'
                                             )])

    buttons += [
        [
            InlineKeyboardButton(text='Нет моих компетенций 😕',
                                 callback_data=command_constants.COMMAND__NO_RELEVANT)
        ],
        [
            InlineKeyboardButton(text='Готово 👌', callback_data=command_constants.COMMAND__READY),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    if save_prev_msg:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Чтобы я знал, с какими задачами ты готов помогать, '
                 'выбери свои профессиональные компетенции (можно выбрать '
                 'несколько). После этого, нажми на пункт "Готово 👌"',
            reply_markup=keyboard,
        )
    else:
        update.callback_query.edit_message_text(
            text='Чтобы я знал, с какими задачами ты готов помогать, '
                 'выбери свои профессиональные компетенции (можно выбрать '
                 'несколько). После этого, нажми на пункт "Готово 👌"',
            reply_markup=keyboard,
        )

    return states.CATEGORY


@log_command(command=constants.LOG_COMMANDS_NAME['after_category_choose'])
def after_category_choose(update: Update, context: CallbackContext):   

    user_categories = ', '.join([spec['name'] for spec
                                 in user_db.get_category(update.effective_user.id)
                                 if spec['user_selected']])

    if not user_categories:
        user_categories = 'Категории ещё не выбраны'

    update.callback_query.edit_message_text(
        text=f'Отлично! Теперь я буду присылать тебе уведомления о новых '
             f'заданиях в категориях: *{user_categories}*.\n\n',
        parse_mode=ParseMode.MARKDOWN
    )

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='А пока можешь посмотреть открытые задания.',
        reply_markup=common_comands.get_menu_and_tasks_buttons()
    )

    return states.AFTER_CATEGORY_REPLY


@log_command(command=constants.LOG_COMMANDS_NAME['no_relevant_category'])
def no_relevant_category(update: Update, context: CallbackContext):
    buttons = [
        [
            InlineKeyboardButton(
                text='Предложить компетенции', callback_data=command_constants.COMMAND__ASK_NEW_CATEGORY
            )
        ],
        [
            InlineKeyboardButton(
                text='Посмотреть задания', callback_data=command_constants.COMMAND__OPEN_TASK
            )
        ],
        [
            InlineKeyboardButton(
                text='Вернуться в меню', callback_data=command_constants.COMMAND__OPEN_MENU
            )
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(
        text='Расскажи, какие компетенции нам стоит добавить? '
             'Также ты можешь посмотреть задания в других категориях 😉',
        reply_markup=keyboard
    )

    return states.NO_CATEGORY


@log_command(command=constants.LOG_COMMANDS_NAME['show_open_task'])
def show_open_task(update: Update, context: CallbackContext):
    buttons = [
        [
            InlineKeyboardButton(text='Посмотреть ещё', callback_data=command_constants.COMMAND__OPEN_TASK)
        ],
        [
            InlineKeyboardButton(text='Открыть меню', callback_data=command_constants.COMMAND__OPEN_MENU)
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    if not context.user_data.get(states.START_SHOW_TASK):
        context.user_data[states.START_SHOW_TASK] = []

    tasks = user_db.get_user_active_tasks(
        update.effective_user.id, context.user_data[states.START_SHOW_TASK]
    )
    if tasks:
        tasks.sort(key=lambda x: x[0].id)

    if not tasks:
        update.callback_query.edit_message_text(
            text='Нет доступных заданий',
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text='Открыть меню', callback_data=command_constants.COMMAND__OPEN_MENU)]]
            )
        )
    else:
        for task in tasks[:PAGINATION]:
            """
            Это условия проверяет, является ли элемент последним в списке
            доступных к показу заданий или нет.
            """
            if task[0].id != tasks[-1][0].id:
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=formatter.display_task(task),
                    parse_mode=ParseMode.HTML, disable_web_page_preview=True
                )
                context.user_data[states.START_SHOW_TASK].append(task[0].id)
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=formatter.display_task(task),
                    parse_mode=ParseMode.HTML, disable_web_page_preview=True
                )
                context.user_data[states.START_SHOW_TASK].append(task[0].id)
                update.callback_query.delete_message()
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text='Ты просмотрел все открытые задания на текущий момент.',
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text='Открыть меню',
                                               callback_data=command_constants.COMMAND__OPEN_MENU)]]
                    )
                )
                return states.OPEN_TASKS

        update.callback_query.delete_message()

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Есть ещё задания, показать?',
            reply_markup=keyboard
        )

    return states.OPEN_TASKS


categories_conv = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(choose_category_after_start, pattern='^' + states.GREETING + '$'),
        CallbackQueryHandler(before_confirm_specializations,
                                     pattern='^' + states.GREETING_REGISTERED_USER + '$'),
        CallbackQueryHandler(choose_category, pattern=command_constants.COMMAND__CHANGE_CATEGORY),
        CallbackQueryHandler(show_open_task, pattern=command_constants.COMMAND__OPEN_TASK),
    ],
    states={
       states.GREETING:[
        CallbackQueryHandler(choose_category_after_start, pattern='^' + states.GREETING + '$'),
        CallbackQueryHandler(before_confirm_specializations,
                                     pattern='^' + states.GREETING_REGISTERED_USER + '$')],
       states.CATEGORY: [
                CallbackQueryHandler(choose_category, pattern=command_constants.COMMAND__RETURN_CHOSE_CATEGORY),
                CallbackQueryHandler(after_category_choose, pattern=command_constants.COMMAND__READY),
                CallbackQueryHandler(no_relevant_category, pattern=command_constants.COMMAND__NO_RELEVANT)
            ],
        states.AFTER_CATEGORY_REPLY: [
                CallbackQueryHandler(show_open_task, pattern=command_constants.COMMAND__OPEN_TASK),
                CallbackQueryHandler(common_comands.open_menu, pattern=command_constants.COMMAND__OPEN_MENU)
            ],
        states.NO_CATEGORY: [
                feedback_conv,
                CallbackQueryHandler(show_open_task, pattern=command_constants.COMMAND__OPEN_TASK),
                CallbackQueryHandler(common_comands.open_menu, pattern=command_constants.COMMAND__OPEN_MENU)
            ],
        states.OPEN_TASKS: [
                CallbackQueryHandler(show_open_task, pattern=command_constants.COMMAND__OPEN_TASK),
                CallbackQueryHandler(common_comands.open_menu, pattern=command_constants.COMMAND__OPEN_MENU)
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
