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
                          CallbackQueryHandler)

from bot.states import (GREETING,
                        CATEGORY,
                        AFTER_CATEGORY_REPLY,
                        MENU,
                        OPEN_TASKS,
                        NO_CATEGORY,
                        AFTER_ADD_CATEGORY,
                        AFTER_NEW_QUESTION,
                        AFTER_ADD_FEATURE,
                        TYPING,
                        START_OVER,
                        START_SHOW_TASK,
                        CANCEL_FEEDBACK)

from bot.data_to_db import (add_user,
                            change_subscription,
                            get_tasks,
                            get_category,
                            change_user_category,
                            log_command)
from bot.formatter import display_task
from bot.constants import LOG_COMMANDS_NAME

PAGINATION = 3

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

updater = Updater(token=os.getenv('TOKEN'))

menu_buttons = [
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


@log_command(command=LOG_COMMANDS_NAME['start'], start_menu=True)
def start(update: Update, context: CallbackContext) -> int:
    add_user(update.message)

    button = [
        [
            InlineKeyboardButton(text='Поехали!', callback_data=GREETING)
        ]
    ]
    keyboard = InlineKeyboardMarkup(button)
    update.message.reply_text(
        'Привет! 👋 \n'
        'Я бот ProCharity -онлайн-платформы интеллектуального волонтёрства.'
        'Буду держать тебя в курсе новых задач и помогу оперативно связаться '
        'с командой поддержки.\n\n'
        'Начнём?',
        reply_markup=keyboard
    )

    context.user_data[START_OVER] = False

    return GREETING


@log_command(command=LOG_COMMANDS_NAME['change_user_categories'])
def change_user_categories(update: Update, context: CallbackContext):
    """Auxiliary function for selecting a category and changing the status of subscriptions."""
    pattern_id = re.findall(r'\d+', update.callback_query.data)
    category_id = int(pattern_id[0])
    telegram_id = update.effective_user.id

    change_user_category(telegram_id=telegram_id, category_id=category_id)
    update.callback_query.answer()
    choose_category(update, context)


@log_command(command=LOG_COMMANDS_NAME['choose_category'], ignore_func='change_user_categories')
def choose_category(update: Update, context: CallbackContext):
    """The main function is to select categories for subscribing to them."""

    categories = get_category(update.effective_user.id)

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

    update.callback_query.edit_message_text(
        text='Чтобы я знал, с какими задачами ты готов помогать, '
             'выбери свои профессиональные компетенции (можно выбрать '
             'несколько). После этого, нажми на пункт "Готово 👌"',
        reply_markup=keyboard,
    )
    return CATEGORY


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
    update.callback_query.edit_message_text(
        text='Отлично! Теперь я буду присылать тебе уведомления о новых '
             'заданиях в категориях: <перечень выбранных категорий>.\n\n'
             'А пока можешь посмотреть открытые задания.',
        reply_markup=keyboard
    )
    return AFTER_CATEGORY_REPLY


@log_command(command=LOG_COMMANDS_NAME['open_menu'])
def open_menu(update: Update, context: CallbackContext):
    keyboard = InlineKeyboardMarkup(menu_buttons)
    text = 'Открыть меню'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return MENU


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

    showed = 0
    show_task_now = []

    if not context.user_data.get(START_SHOW_TASK):
        context.user_data[START_SHOW_TASK] = []

    tasks = get_tasks(update.effective_user.id)
    if tasks:
        tasks.sort(key=lambda x: x[0].id)
        for task in tasks:
            if task[0].id not in context.user_data[START_SHOW_TASK] and showed != PAGINATION:
                context.user_data[START_SHOW_TASK].append(task[0].id)
                show_task_now.append(task)
                showed += 1

    if not show_task_now:
        update.callback_query.edit_message_text(
            text='Нет доступных заданий',
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text='Открыть меню', callback_data='open_menu')]]
            )
        )
    elif len(show_task_now) == 1:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=display_task(show_task_now[0]), parse_mode=ParseMode.HTML
        )
        update.callback_query.delete_message()

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Нет доступных заданий',
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text='Открыть меню', callback_data='open_menu')]]
            )
        )
    else:
        for task in show_task_now[:PAGINATION]:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=display_task(task), parse_mode=ParseMode.HTML
            )

        update.callback_query.delete_message()

        context.bot.send_message(
            chat_id=update.effective_chat.id, text='Есть ещё задания, показать?', parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )

    return OPEN_TASKS


@log_command(command=LOG_COMMANDS_NAME['send_task_to_friend'])
def send_task_to_friend(update: Update, context: CallbackContext):
    pass


@log_command(command=LOG_COMMANDS_NAME['ask_question'])
def ask_question(update: Update, context: CallbackContext):
    button = [
        [InlineKeyboardButton(text='Вернуться в меню', callback_data='open_menu')]
    ]
    keyboard = InlineKeyboardMarkup(button)
    update.callback_query.edit_message_text(
        text='Напишите свой вопрос', reply_markup=keyboard
    )

    return AFTER_NEW_QUESTION


@log_command(command=LOG_COMMANDS_NAME['after_ask_question'])
def after_ask_question(update: Update, context: CallbackContext):
    buttons = [
        [
            InlineKeyboardButton(text='Посмотреть открытые задания', callback_data='open_task')
        ],
        [
            InlineKeyboardButton(text='Открыть меню', callback_data='open_menu')
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text='Спасибо, я уже передал информацию коллегам! '
             'Ответ придёт на твою почту <почта волонтёра>',
        reply_markup=keyboard
    )

    return AFTER_CATEGORY_REPLY


@log_command(command=LOG_COMMANDS_NAME['no_relevant_category'])
def no_relevant_category(update: Update, context: CallbackContext):
    buttons = [
        [
            InlineKeyboardButton(
                text='Предложить компетенции', callback_data='add_new_category'
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

    return NO_CATEGORY


@log_command(command=LOG_COMMANDS_NAME['email_feedback'])
def email_feedback(update: Update, context: CallbackContext):
    button = [
        [
            InlineKeyboardButton(text='Вернуться в меню', callback_data='open_menu')
        ]
    ]
    keyboard = InlineKeyboardMarkup(button)
    update.callback_query.edit_message_text(
        text='Будем рады ответить на любые вопросы по '
             'почте procharity@friends-foundation.com',
        reply_markup=keyboard
    )

    return MENU


@log_command(command=LOG_COMMANDS_NAME['add_new_category'])
def add_new_category(update: Update, context: CallbackContext):
    button = [
        [InlineKeyboardButton(text='Вернуться в меню', callback_data='open_menu')]
    ]
    keyboard = InlineKeyboardMarkup(button)
    update.callback_query.edit_message_text(
        text='Напиши, в какой профессиональной сфере ты бы хотел помогать?',
        reply_markup=keyboard
    )

    return AFTER_ADD_CATEGORY


@log_command(command=LOG_COMMANDS_NAME['after_add_new_category'])
def after_add_new_category(update: Update, context: CallbackContext):
    buttons = [
        [
            InlineKeyboardButton(text='Посмотреть открытые задания', callback_data='open_task')
        ],
        [
            InlineKeyboardButton(text='Открыть меню', callback_data='open_menu')
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(
        text='Спасибо, я передал информацию команде ProCharity!'
             'Ответ придет на почту <email волонтера>',
        reply_markup=keyboard
    )

    return AFTER_ADD_CATEGORY


@log_command(command=LOG_COMMANDS_NAME['add_new_feature'])
def add_new_feature(update: Update, context: CallbackContext):
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text='Расскажи, какого функционала тебе не хватает?'
    )

    return TYPING


@log_command(command=LOG_COMMANDS_NAME['after_add_new_feature'])
def after_add_new_feature(update: Update, context: CallbackContext):
    buttons = [
        [
            InlineKeyboardButton(text='Посмотреть открытые задания', callback_data='open_task')
        ],
        [
            InlineKeyboardButton(text='Открыть меню', callback_data='open_menu')
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(
        text='Спасибо, я уже передал информацию коллегам! '
             'Ответ придёт на твою почту <почта волонтёра>',
        reply_markup=keyboard
    )

    return AFTER_ADD_FEATURE


@log_command(command=LOG_COMMANDS_NAME['about'])
def about(update: Update, context: CallbackContext):
    button = [
        [InlineKeyboardButton(text='Вернуться в меню', callback_data='open_menu')]
    ]
    keyboard = InlineKeyboardMarkup(button)
    update.callback_query.edit_message_text(
        text='С ProCharity профессионалы могут помочь некоммерческим '
             'организациям в вопросах, которые требуют специальных знаний и '
             'опыта. Интеллектуальный волонтёр безвозмездно дарит фонду своё '
             'время и профессиональные навыки, позволяя решать задачи, '
             'которые трудно закрыть силами штатных сотрудников.',
        reply_markup=keyboard
    )

    return MENU


@log_command(command=LOG_COMMANDS_NAME['stop_task_subscription'])
def stop_task_subscription(update: Update, context: CallbackContext):
    new_mailing_status = change_subscription(update.effective_user.id)
    cancel_feedback_buttons = [
        [
            InlineKeyboardButton(
                text='Слишком много уведомлений',
                callback_data='many_notification'
            )
        ],
        [
            InlineKeyboardButton(
                text='Нет времени на волонтёрство',
                callback_data='no_time'
            )
        ],
        [
            InlineKeyboardButton(
                text='Нет подходящих заданий',
                callback_data='no_relevant_task'
            )
        ],
        [
            InlineKeyboardButton(
                text='Бот мне не удобен',
                callback_data='bot_is_bad'
            )
        ],
        [
            InlineKeyboardButton(
                text='Фонды меня не выбирают',
                callback_data='fond_ignore'
            )
        ],
        [
            InlineKeyboardButton(text='Другое', callback_data='another')
        ],
    ]
    cancel_feedback_keyboard = InlineKeyboardMarkup(cancel_feedback_buttons)

    button = [
        [
            InlineKeyboardButton(
                text='Вернуться в меню', callback_data='open_menu'
            )
        ],
        [
            InlineKeyboardButton(
                text='Открыть меню', callback_data='open_menu'
            )
        ]
    ]
    keyboard = InlineKeyboardMarkup(button)

    if new_mailing_status:
        answer = 'Отлично! Теперь я буду присылать тебе уведомления о новых ' \
                 'заданиях в категориях: <перечень выбранных категорий>.\n\n' \
                 'А пока можешь посмотреть открытые задания.'

        update.callback_query.edit_message_text(text=answer,
                                                reply_markup=keyboard
                                                )

        return AFTER_CATEGORY_REPLY

    else:
        answer = 'Ты больше не будешь получать новые задания от фондов, но ' \
                 'всегда сможешь найти их на сайте https://procharity.ru'

        update.callback_query.edit_message_text(
            text=answer, reply_markup=cancel_feedback_keyboard
        )

    return CANCEL_FEEDBACK


def cancel_feedback(update: Update, context: CallbackContext):
    keyboard = InlineKeyboardMarkup(menu_buttons)
    update.callback_query.edit_message_text(
        text='Спасибо, я передал информацию команде ProCharity!',
        reply_markup=keyboard
    )

    return MENU


@log_command(command=LOG_COMMANDS_NAME['cancel'])
def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GREETING: [
                CallbackQueryHandler(choose_category, pattern='^' + GREETING + '$')
            ],
            CATEGORY: [
                CallbackQueryHandler(choose_category, pattern='^return_chose_category$'),
                CallbackQueryHandler(after_category_choose, pattern='^ready$'),
                CallbackQueryHandler(no_relevant_category, pattern='^no_relevant$')

            ],
            AFTER_CATEGORY_REPLY: [
                CallbackQueryHandler(show_open_task, pattern='^open_task$'),
                CallbackQueryHandler(open_menu, pattern='^open_menu$')
            ],
            MENU: [
                CallbackQueryHandler(show_open_task, pattern='^open_task$'),
                CallbackQueryHandler(email_feedback, pattern='^ask_question$'),
                CallbackQueryHandler(about, pattern='^about$'),
                CallbackQueryHandler(choose_category, pattern='^change_category$'),
                CallbackQueryHandler(email_feedback, pattern='^new_feature$'),
                CallbackQueryHandler(stop_task_subscription, pattern='^stop_subscription'),
                CallbackQueryHandler(open_menu, pattern='^open_menu$')
            ],
            OPEN_TASKS: [
                CallbackQueryHandler(show_open_task, pattern='^open_task$'),
                CallbackQueryHandler(send_task_to_friend, pattern='^send_task$'),
                CallbackQueryHandler(open_menu, pattern='^open_menu$')
            ],
            NO_CATEGORY: [
                CallbackQueryHandler(email_feedback, pattern='^add_new_category$'),
                CallbackQueryHandler(show_open_task, pattern='^open_task$'),
                CallbackQueryHandler(open_menu, pattern='^open_menu$')
            ],
            AFTER_ADD_CATEGORY: [
                CallbackQueryHandler(open_menu, pattern='^open_menu$')
            ],
            AFTER_NEW_QUESTION: [
                CallbackQueryHandler(email_feedback, pattern='^open_menu$')
            ],
            AFTER_ADD_FEATURE: [
                CallbackQueryHandler(email_feedback, pattern='^open_menu$')
            ],
            CANCEL_FEEDBACK: [
                CallbackQueryHandler(cancel_feedback, pattern='^many_notification$'),
                CallbackQueryHandler(cancel_feedback, pattern='^no_time$'),
                CallbackQueryHandler(cancel_feedback, pattern='^no_relevant_task$'),
                CallbackQueryHandler(cancel_feedback, pattern='^bot_is_bad$'),
                CallbackQueryHandler(cancel_feedback, pattern='^fond_ignore'),
                CallbackQueryHandler(cancel_feedback, pattern='^another')
            ]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    update_users_category = CallbackQueryHandler(change_user_categories, pattern='^up_cat[0-9]{1,2}$')

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(update_users_category)
    updater.start_polling()
