import logging
import os

from dotenv import load_dotenv
from telegram import (Update,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton,
                      ParseMode)
from telegram.ext import (Updater,
                          CommandHandler,
                          ConversationHandler,
                          CallbackContext,
                          CallbackQueryHandler,
                          PicklePersistence)

from app.config import BOT_PERSISTENCE_FILE

from bot import states
from bot import common_comands
from bot import constants
from bot import formatter
from bot import categories_selection
from bot.handlers.feedback_handler import feedback_conv
from bot.handlers.stop_subscription_handler import stop_subscription_conv
from bot.logger import log_command
from bot.user_db import UserDB


PAGINATION = 3

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

bot_persistence = PicklePersistence(filename=BOT_PERSISTENCE_FILE,
                                    store_bot_data=True,
                                    store_user_data=True,
                                    store_callback_data=True,
                                    store_chat_data=True)

updater = Updater(token=os.getenv('TOKEN'), persistence=bot_persistence, use_context=True)

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

@log_command(command=constants.LOG_COMMANDS_NAME['show_open_task'])
def show_open_task(update: Update, context: CallbackContext):
    buttons = [
        [
            InlineKeyboardButton(text='Посмотреть ещё', callback_data='open_task')
        ],
        [
            InlineKeyboardButton(text='Открыть меню', callback_data='open_menu')
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
                [[InlineKeyboardButton(text='Открыть меню', callback_data='open_menu')]]
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
                                               callback_data='open_menu')]]
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


@log_command(command=constants.LOG_COMMANDS_NAME['about'])
def about(update: Update, context: CallbackContext):
    button = [
        [InlineKeyboardButton(text='Вернуться в меню', callback_data='open_menu')]
    ]
    keyboard = InlineKeyboardMarkup(button)
    update.callback_query.edit_message_text(
        text='С ProCharity профессионалы могут помочь некоммерческим '
             'организациям в вопросах, которые требуют специальных знаний и '
             'опыта.\n\nИнтеллектуальный волонтёр безвозмездно дарит фонду своё '
             'время и профессиональные навыки, позволяя решать задачи, '
             'которые трудно закрыть силами штатных сотрудников.',
        reply_markup=keyboard
    )

    return states.MENU


def error_handler(update: object, context: CallbackContext) -> None:
    text = (f"Error '{context.error}', user id: {update.effective_user.id},")
    logger.error(msg=text, exc_info=context.error)


def init() -> None:
    dispatcher = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', common_comands.start)
        ],
        states={
            states.GREETING: [
                CallbackQueryHandler(categories_selection.choose_category_after_start, pattern='^' + states.GREETING + '$'),
                CallbackQueryHandler(categories_selection.before_confirm_specializations,
                                     pattern='^' + states.GREETING_REGISTERED_USER + '$')
            ],
            states.CATEGORY: [
                CallbackQueryHandler(categories_selection.choose_category, pattern='^return_chose_category$'),
                CallbackQueryHandler(categories_selection.after_category_choose, pattern='^ready$'),
                CallbackQueryHandler(categories_selection.no_relevant_category, pattern='^no_relevant$')

            ],
            states.AFTER_CATEGORY_REPLY: [
                CallbackQueryHandler(show_open_task, pattern='^open_task$'),
                CallbackQueryHandler(common_comands.open_menu, pattern='^open_menu$')
            ],
            states.MENU: [
                CallbackQueryHandler(show_open_task, pattern='^open_task$'),
                feedback_conv,
                CallbackQueryHandler(about, pattern='^about$'),
                CallbackQueryHandler(categories_selection.choose_category, pattern='^change_category$'),
                stop_subscription_conv,
                CallbackQueryHandler(start_task_subscription, pattern='^start_subscription$'),
                CallbackQueryHandler(common_comands.open_menu, pattern='^open_menu$')
            ],
            states.OPEN_TASKS: [
                CallbackQueryHandler(show_open_task, pattern='^open_task$'),
                CallbackQueryHandler(common_comands.open_menu, pattern='^open_menu$')
            ],
            states.NO_CATEGORY: [
                feedback_conv,
                CallbackQueryHandler(show_open_task, pattern='^open_task$'),
                CallbackQueryHandler(common_comands.open_menu, pattern='^open_menu$')
            ]           
        },
        fallbacks=[
            CommandHandler('start', common_comands.start),
            CommandHandler('menu', common_comands.open_menu_fall)
        ],
        persistent=True,
        name='conv_handler'
    )

    update_users_category = CallbackQueryHandler(categories_selection.change_user_categories, pattern='^up_cat[0-9]{1,2}$')

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(update_users_category)
    dispatcher.add_error_handler(error_handler)
    updater.start_polling()
