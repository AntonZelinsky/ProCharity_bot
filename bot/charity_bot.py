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
                            get_tasks,
                            get_category,
                            change_user_category,
                            log_command)
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

log_commands_name = {
    'start': 'Старт',
    'change_user_categories': 'Изменение категории',
    'choose_category': 'Меню выбора категории',
    'after_category_choose': 'Готово',
    'open_menu': 'Открыть меню',
    'show_open_task': 'Посмотреть открытые задания',
    'send_task_to_friend': 'Переслать задание другу',
    'ask_question': 'Задать вопрос',
    'after_ask_question': 'Меню после вопроса',
    'no_relevant_category': 'Моих компетенций здесь нет',
    'email_feedback': 'Отправка емейла',
    'add_new_category': 'Добавление новой категории',
    'after_add_new_category': 'Меню после добавления новой категории',
    'add_new_feature': 'Хочу новый функционал бота',
    'after_add_new_feature': 'Меню после добавление функционала',
    'about': 'О платформе',
    'stop_task_subscription': 'Остановить/включить подписку на задания',
    'cancel': 'Отмена',

}


@log_command(command=log_commands_name['start'], start_menu=True)
def start(update: Update, context: CallbackContext) -> int:
    add_user(update.message)

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


@log_command(command=log_commands_name['change_user_categories'])
def change_user_categories(update: Update, context: CallbackContext):
    """Auxiliary function for selecting a category and changing the status of subscriptions."""
    pattern_id = re.findall(r'\d+', update.callback_query.data)
    category_id = int(pattern_id[0])
    telegram_id = update.effective_user.id

    change_user_category(telegram_id=telegram_id, category_id=category_id)

    choose_category(update, context)


@log_command(command=log_commands_name['choose_category'], ignore_func='change_user_categories')
def choose_category(update: Update, context: CallbackContext):
    """The main function is to select categories for subscribing to them."""
    # if log:
    #   log_command(update.effective_user.id, choose_category.__name__)

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


@log_command(command=log_commands_name['after_category_choose'])
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
        text='Ура! Теперь ты будешь получать новые задания по твоим компетенциям.'
             'А пока можешь посмотреть открытые задания.',
        reply_markup=keyboard
    )
    return AFTER_CATEGORY_REPLY


@log_command(command=log_commands_name['open_menu'])
def open_menu(update: Update, context: CallbackContext):
    keyboard = InlineKeyboardMarkup(menu_buttons)
    text = 'Menu'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return MENU


@log_command(command=log_commands_name['show_open_task'])
def show_open_task(update: Update, context: CallbackContext):
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

    update.callback_query.delete_message()

    context.bot.send_message(
        chat_id=update.effective_chat.id, text=display_task(tasks[2]), parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
    )

    return OPEN_TASKS


@log_command(command=log_commands_name['send_task_to_friend'])
def send_task_to_friend(update: Update, context: CallbackContext):
    pass


@log_command(command=log_commands_name['ask_question'])
def ask_question(update: Update, context: CallbackContext):
    button = [
        [InlineKeyboardButton(text='Вернуться в меню', callback_data='open_menu')]
    ]
    keyboard = InlineKeyboardMarkup(button)
    update.callback_query.edit_message_text(
        text='Напишите свой вопрос', reply_markup=keyboard
    )

    return AFTER_NEW_QUESTION


@log_command(command=log_commands_name['after_ask_question'])
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
        text='Спасибо, я уже передал информацию коллегам! Ответ придёт на твою почту <почта волонтёра>',
        reply_markup=keyboard
    )

    return AFTER_CATEGORY_REPLY


@log_command(command=log_commands_name['no_relevant_category'])
def no_relevant_category(update: Update, context: CallbackContext):
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


@log_command(command=log_commands_name['email_feedback'])
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


@log_command(command=log_commands_name['add_new_category'])
def add_new_category(update: Update, context: CallbackContext):
    button = [
        [InlineKeyboardButton(text='Вернуться в меню', callback_data='open_menu')]
    ]
    keyboard = InlineKeyboardMarkup(button)
    update.callback_query.edit_message_text(
        text='Напиши, в какой профессиональной сфере ты бы хотел помогать',
        reply_markup=keyboard
    )

    return AFTER_ADD_CATEGORY


@log_command(command=log_commands_name['after_add_new_category'])
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
        text='Спасибо, я уже передал информацию коллегам! '
             'Ответ придёт на твою почту <почта волонтёра>',
        reply_markup=keyboard
    )

    return AFTER_ADD_CATEGORY


@log_command(command=log_commands_name['add_new_feature'])
def add_new_feature(update: Update, context: CallbackContext):
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text='Напиши, какого функционала в боте тебе не хватает?'
    )

    return TYPING


@log_command(command=log_commands_name['after_add_new_feature'])
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


@log_command(command=log_commands_name['about'])
def about(update: Update, context: CallbackContext):
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


@log_command(command=log_commands_name['stop_task_subscription'])
def stop_task_subscription(update: Update, context: CallbackContext):
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


@log_command(command=log_commands_name['cancel'])
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
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )
    update_users_category = CallbackQueryHandler(change_user_categories, pattern='^up_cat[0-9]{1,2}$')

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(update_users_category)
    updater.start_polling()
