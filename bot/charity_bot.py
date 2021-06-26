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
                        START_OVER)

from bot.data_to_db import (add_user,
                            change_subscription,
                            log_command,
                            get_tasks,
                            get_category,
                            change_category_subscription)
from bot.formatter import display_task

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

updater = Updater(token=os.getenv('TOKEN'))

menu_buttons = [
    [
        InlineKeyboardButton(text='Посмотреть открытые задания', callback_data='open_task')
    ],
    [
        InlineKeyboardButton(text='Задать вопрос', callback_data='ask_question')
    ],
    [
        InlineKeyboardButton(text='О платформе', callback_data='about')
    ],
    [
        InlineKeyboardButton(text='Изменить компетенции', callback_data='change_category')
    ],
    [
        InlineKeyboardButton(text='Хочу новый функционал бота', callback_data='new_feature')
    ],
    [
        InlineKeyboardButton(text='Остановить/включить подписку на задания', callback_data='stop_subscription')
    ]
]


def start(update: Update, context: CallbackContext) -> int:
    add_user(update.message)
    log_command(update.effective_user.id, start.__name__)

    button = [
        [
            InlineKeyboardButton(text='Поехали!', callback_data=GREETING)
        ]
    ]
    keyboard = InlineKeyboardMarkup(button)
    update.message.reply_text(
        'Привет! Я - бот '
        'ProCharity-онлайн-платформы интеллектуального волонтёрства!'
        'Помогу тебе быть в курсе интересных задач и буду напоминать '
        'о текущих задачах.'
        'Давай начнём прямо сейчас?',
        reply_markup=keyboard
    )

    context.user_data[START_OVER] = False

    return GREETING


def change_user_categories(update: Update, context: CallbackContext):
    """Auxiliary function for selecting a category and changing the status of subscriptions."""
    log_command(update.effective_user.id, change_user_categories.__name__)
    pattern_id = re.findall(r'\d+', update.callback_query.data)
    category_id = int(pattern_id[0])
    telegram_id = update.effective_user.id

    change_category_subscription(telegram_id=telegram_id, category_id=category_id)

    choose_category(update, context)


def choose_category(update: Update, context: CallbackContext):
    """The main function is to select categories for subscribing to them."""
    log_command(update.effective_user.id, choose_category.__name__)
    categories = get_category(update.effective_user.id)

    buttons = []
    for cat in categories:
        if cat['user_selected']:
            cat['name'] += "✅"
        buttons.append([InlineKeyboardButton(text=cat['name'], callback_data=f'up_cat{cat["category_id"]}'
                                             )])

    buttons += [
        [
            InlineKeyboardButton(text='Готово!', callback_data='ready'),
        ],
        [
            InlineKeyboardButton(text='Моих компетенций здесь нет', callback_data='no_relevant')
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.edit_message_text(
        text='Чтобы я знал, в каких задачах ты можешь помогать фондам выбери свои профессиональные компетенции:',
        reply_markup=keyboard,
    )
    return CATEGORY


def after_category_choose(update: Update, context: CallbackContext):
    log_command(update.effective_user.id, after_category_choose.__name__)

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
        text='Ура! Теперь ты будешь получать новые задания по твоим компетенциям.'
             'А пока можешь посмотреть открытые задания.',
        reply_markup=keyboard
    )
    return AFTER_CATEGORY_REPLY


def open_menu(update: Update, context: CallbackContext):
    log_command(update.effective_user.id, open_menu.__name__)

    keyboard = InlineKeyboardMarkup(menu_buttons)
    text = 'Menu'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return MENU


def show_open_task(update: Update, context: CallbackContext):
    log_command(update.effective_user.id, show_open_task.__name__)

    tasks = get_tasks(update.effective_user.id)

    buttons = [
        [
            InlineKeyboardButton(text='Посмотреть ещё', callback_data='open_task')
        ],
        # [
        #     InlineKeyboardButton(text='Переслать задание другу', callback_data='send_task')
        # ],
        [
            InlineKeyboardButton(text='Открыть меню', callback_data='open_menu')
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    for task in tasks[0:2]:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text=display_task(task), parse_mode=ParseMode.MARKDOWN
        )

    for task in tasks[2]:
        update.callback_query.edit_message_text(
            display_task(task),
            reply_markup=keyboard
        )
    return OPEN_TASKS


def send_task_to_friend(update: Update, context: CallbackContext):
    log_command(update.effective_user.id, send_task_to_friend.__name__)
    pass


def ask_question(update: Update, context: CallbackContext):
    log_command(update.effective_user.id, ask_question.__name__)

    button = [
        [InlineKeyboardButton(text='Вернуться в меню', callback_data='open_menu')]
    ]
    keyboard = InlineKeyboardMarkup(button)
    update.callback_query.edit_message_text(
        text='Напишите свой вопрос', reply_markup=keyboard
    )

    return AFTER_NEW_QUESTION


def after_ask_question(update: Update, context: CallbackContext):
    log_command(update.effective_user.id, after_ask_question.__name__)

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
        text='Спасибо, я уже передал информацию коллегам! Ответ придёт на твою почту <почта волонтёра>',
        reply_markup=keyboard
    )

    return AFTER_CATEGORY_REPLY


def no_relevant_category(update: Update, context: CallbackContext):
    log_command(update.effective_user.id, no_relevant_category.__name__)

    buttons = [
        [
            InlineKeyboardButton(text='Написать, какие компетенции добавить', callback_data='add_new_category')
        ],
        [
            InlineKeyboardButton(text='Посмотреть другие задания', callback_data='open_task')
        ],
        [
            InlineKeyboardButton(text='Вернуться в меню', callback_data='open_menu')
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(
        text='Очень жаль!\n\nТы можешь посмотреть задания '
             'в других категориях или поделиться с нами, '
             'какие компетенции нам следует добавить.',
        reply_markup=keyboard
    )

    return NO_CATEGORY


def email_feedback(update: Update, context: CallbackContext):
    log_command(update.effective_user.id, email_feedback.__name__)
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


def add_new_category(update: Update, context: CallbackContext):
    log_command(update.effective_user.id, add_new_category.__name__)

    button = [
        [InlineKeyboardButton(text='Вернуться в меню', callback_data='open_menu')]
    ]
    keyboard = InlineKeyboardMarkup(button)
    update.callback_query.edit_message_text(
        text='Напиши, в какой профессиональной сфере ты бы хотел помогать',
        reply_markup=keyboard
    )

    return AFTER_ADD_CATEGORY


def after_add_new_category(update: Update, context: CallbackContext):
    log_command(update.effective_user.id, after_add_new_category.__name__)

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

    return AFTER_ADD_CATEGORY


def add_new_feature(update: Update, context: CallbackContext):
    log_command(update.effective_user.id, add_new_feature.__name__)

    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text='Напиши, какого функционала в боте тебе не хватает?'
    )

    return TYPING


def after_add_new_feature(update: Update, context: CallbackContext):
    log_command(update.effective_user.id, after_add_new_feature.__name__)

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


def about(update: Update, context: CallbackContext):
    log_command(update.effective_user.id, about.__name__)

    button = [
        [InlineKeyboardButton(text='Вернуться в меню', callback_data='open_menu')]
    ]
    keyboard = InlineKeyboardMarkup(button)
    update.callback_query.edit_message_text(
        text='ProCharity - это возможность для профессионалов своего дела помочь '
             'некоммерческим организациям в вопросах, которые требуют специального '
             'знания и опыта. Интеллектуальный волонтёр безвозмездно дарит фонду '
             'время и профессиональные навыки, позволяя решать задачи, которые '
             'трудно бывает закрыть силами штатных сотрудников. А фонд благодаря '
             'ему получает квалифицированную практическую помощь в решении '
             'накопившихся задач.'
             ' http://procharity.ru',
        reply_markup=keyboard
    )

    return MENU


# TODO Переименовать функцию на change_task_subscription
def stop_task_subscription(update: Update, context: CallbackContext):
    log_command(update.effective_user.id, stop_task_subscription.__name__)
    new_mailing_status = change_subscription(update.effective_user.id)

    button = [
        [InlineKeyboardButton(text='Вернуться в меню', callback_data='open_menu')]
    ]
    keyboard = InlineKeyboardMarkup(button)

    if new_mailing_status:
        answer = 'Ура! Теперь ты будешь получать новые задания по твоим компетенциям.' \
                 ' А пока можешь посмотреть открытые задания.'

        update.callback_query.edit_message_text(text=answer,
                                                # reply_markup=ReplyKeyboardMarkup(markup, one_time_keyboard=True)
                                                reply_markup=keyboard
                                                )

        return AFTER_CATEGORY_REPLY

    else:
        answer = 'Теперь ты не будешь получать новые задания от фондов, но всегда ' \
                 'можешь найти их на сайте http://procharity.ru'

        update.callback_query.edit_message_text(text=answer,
                                                # reply_markup=ReplyKeyboardMarkup(markup, one_time_keyboard=True)
                                                reply_markup=keyboard
                                                )

    return MENU


def cancel(update: Update, context: CallbackContext):
    log_command(update.effective_user.id, cancel.__name__)

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
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    update_users_category = CallbackQueryHandler(change_user_categories, pattern='^up_cat[0-9]{1,2}$')

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(update_users_category)
    updater.start_polling()
