import logging
import os
import re

from dotenv import load_dotenv
from telegram import (ReplyKeyboardRemove,
                      Update,
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
from bot.common_comands import (open_menu, open_menu_fall,
                                get_subscription_button, start,
                                MENU_BUTTONS)
from bot.constants import LOG_COMMANDS_NAME, REASONS
from bot.formatter import display_task
from bot.handlers.feedback_handler import feedback_conv
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


def choose_category_after_start(update: Update, context: CallbackContext):
    update.callback_query.edit_message_text(
        text=update.callback_query.message.text
    )
    return choose_category(update, context, True)


def before_confirm_specializations(update: Update, context: CallbackContext):
    update.callback_query.edit_message_text(
        text=update.callback_query.message.text
    )
    return confirm_specializations(update, context)


@log_command(command=LOG_COMMANDS_NAME['confirm_specializations'])
def confirm_specializations(update: Update, context: CallbackContext):
    buttons = [
        [
            InlineKeyboardButton(text='Да', callback_data='ready')
        ],
        [
            InlineKeyboardButton(text='Нет, хочу изменить.', callback_data='return_chose_category')
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


@log_command(command=LOG_COMMANDS_NAME['change_user_categories'])
def change_user_categories(update: Update, context: CallbackContext):
    """Auxiliary function for selecting a category and changing the status of subscriptions."""
    pattern_id = re.findall(r'\d+', update.callback_query.data)
    category_id = int(pattern_id[0])
    telegram_id = update.effective_user.id

    user_db.change_user_category(telegram_id=telegram_id, category_id=category_id)
    choose_category(update, context)
    update.callback_query.answer()


@log_command(command=LOG_COMMANDS_NAME['choose_category'],
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
                                 callback_data='no_relevant')
        ],
        [
            InlineKeyboardButton(text='Готово 👌', callback_data='ready'),
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


@log_command(command=LOG_COMMANDS_NAME['after_category_choose'])
def after_category_choose(update: Update, context: CallbackContext):
    buttons = [
        [
            InlineKeyboardButton(text='Посмотреть открытые задания', callback_data='open_task')
        ],
        [
            InlineKeyboardButton(text='Открыть меню', callback_data='open_menu')
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

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
        reply_markup=keyboard
    )

    return states.AFTER_CATEGORY_REPLY


@log_command(command=LOG_COMMANDS_NAME['show_open_task'])
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
                    chat_id=update.effective_chat.id, text=display_task(task),
                    parse_mode=ParseMode.HTML, disable_web_page_preview=True
                )
                context.user_data[states.START_SHOW_TASK].append(task[0].id)
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=display_task(task),
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


@log_command(command=LOG_COMMANDS_NAME['no_relevant_category'])
def no_relevant_category(update: Update, context: CallbackContext):
    buttons = [
        [
            InlineKeyboardButton(
                text='Предложить компетенции', callback_data='ask_new_category'
            )
        ],
        [
            InlineKeyboardButton(
                text='Посмотреть задания', callback_data='open_task'
            )
        ],
        [
            InlineKeyboardButton(
                text='Вернуться в меню', callback_data='open_menu'
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


@log_command(command=LOG_COMMANDS_NAME['about'])
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


@log_command(command=LOG_COMMANDS_NAME['stop_task_subscription'])
def stop_task_subscription(update: Update, context: CallbackContext):
    context.user_data[states.SUBSCRIPTION_FLAG] = user_db.change_subscription(update.effective_user.id)
    cancel_feedback_buttons = [
        [
            InlineKeyboardButton(text=reason[1], callback_data=reason[0])
        ] for reason in REASONS.items()
    ]

    cancel_feedback_keyboard = InlineKeyboardMarkup(cancel_feedback_buttons)

    answer = ('Ты больше не будешь получать новые задания от фондов, но '
              'всегда сможешь найти их на сайте https://procharity.ru\n\n'
              'Поделись, пожалуйста, почему ты решил отписаться?')

    update.callback_query.edit_message_text(
        text=answer, reply_markup=cancel_feedback_keyboard, disable_web_page_preview=True
    )

    return states.CANCEL_FEEDBACK


@log_command(command=LOG_COMMANDS_NAME['start_task_subscription'])
def start_task_subscription(update: Update, context: CallbackContext):
    context.user_data[states.SUBSCRIPTION_FLAG] = user_db.change_subscription(update.effective_user.id)

    button = [
        [
            InlineKeyboardButton(
                text='Посмотреть открытые задания', callback_data='open_task'
            )
        ],
        [
            InlineKeyboardButton(
                text='Открыть меню', callback_data='open_menu'
            )
        ]
    ]
    keyboard = InlineKeyboardMarkup(button)

    user_categories = [
        c['name'] for c in user_db.get_category(update.effective_user.id)
        if c['user_selected']
    ]

    answer = f'Отлично! Теперь я буду присылать тебе уведомления о ' \
             f'новых заданиях в ' \
             f'категориях: {", ".join(user_categories)}.\n\n' \
             f'А пока можешь посмотреть открытые задания.'

    update.callback_query.edit_message_text(text=answer,
                                            reply_markup=keyboard)

    return states.AFTER_CATEGORY_REPLY


@log_command(command=LOG_COMMANDS_NAME['cancel_feedback'])
def cancel_feedback(update: Update, context: CallbackContext):
    subscription_button = get_subscription_button(context)
    reason_canceling = update['callback_query']['data']
    telegram_id = update['callback_query']['message']['chat']['id']
    user_db.cancel_feedback_stat(telegram_id, reason_canceling)
    MENU_BUTTONS[-1] = [subscription_button]
    keyboard = InlineKeyboardMarkup(MENU_BUTTONS)
    update.callback_query.edit_message_text(
        text='Спасибо, я передал информацию команде ProCharity!',
        reply_markup=keyboard
    )

    return states.MENU


@log_command(command=LOG_COMMANDS_NAME['cancel'])
def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def error_handler(update: object, context: CallbackContext) -> None:
    text = (f"Error '{context.error}', user id: {update.effective_user.id},")
    logger.error(msg=text, exc_info=context.error)


def main() -> None:
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start)
        ],
        states={
            states.GREETING: [
                CallbackQueryHandler(choose_category_after_start, pattern='^' + states.GREETING + '$'),
                CallbackQueryHandler(before_confirm_specializations,
                                     pattern='^' + states.GREETING_REGISTERED_USER + '$')
            ],
            states.CATEGORY: [
                CallbackQueryHandler(choose_category, pattern='^return_chose_category$'),
                CallbackQueryHandler(after_category_choose, pattern='^ready$'),
                CallbackQueryHandler(no_relevant_category, pattern='^no_relevant$')

            ],
            states.AFTER_CATEGORY_REPLY: [
                CallbackQueryHandler(show_open_task, pattern='^open_task$'),
                CallbackQueryHandler(open_menu, pattern='^open_menu$')
            ],
            states.MENU: [
                CallbackQueryHandler(show_open_task, pattern='^open_task$'),
                feedback_conv,
                CallbackQueryHandler(about, pattern='^about$'),
                CallbackQueryHandler(choose_category, pattern='^change_category$'),
                CallbackQueryHandler(stop_task_subscription, pattern='^stop_subscription$'),
                CallbackQueryHandler(start_task_subscription, pattern='^start_subscription$'),
                CallbackQueryHandler(open_menu, pattern='^open_menu$')
            ],
            states.OPEN_TASKS: [
                CallbackQueryHandler(show_open_task, pattern='^open_task$'),
                CallbackQueryHandler(open_menu, pattern='^open_menu$')
            ],
            states.NO_CATEGORY: [
                feedback_conv,
                CallbackQueryHandler(show_open_task, pattern='^open_task$'),
                CallbackQueryHandler(open_menu, pattern='^open_menu$')
            ],
            states.CANCEL_FEEDBACK: [
                CallbackQueryHandler(cancel_feedback, pattern='^many_notification$'),
                CallbackQueryHandler(cancel_feedback, pattern='^no_time$'),
                CallbackQueryHandler(cancel_feedback, pattern='^no_relevant_task$'),
                CallbackQueryHandler(cancel_feedback, pattern='^bot_is_bad$'),
                CallbackQueryHandler(cancel_feedback, pattern='^fond_ignore'),
                CallbackQueryHandler(cancel_feedback, pattern='^another')
            ]
        },

        fallbacks=[
            CommandHandler('start', start),
            CommandHandler('menu', open_menu_fall)
        ],
        persistent=True,
        name='conv_handler'
    )
    dispatcher.add_handler(CommandHandler('cancel', cancel))

    update_users_category = CallbackQueryHandler(change_user_categories, pattern='^up_cat[0-9]{1,2}$')

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(update_users_category)
    dispatcher.add_error_handler(error_handler)
    updater.start_polling()
