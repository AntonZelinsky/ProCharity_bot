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
                        START_SHOW_TASK,
                        CANCEL_FEEDBACK,
                        SUBSCRIPTION_FLAG,
                        GREETING_REGISTERED_USER,
                        )

from bot.data_to_db import (add_user,
                            change_subscription,
                            get_user_active_tasks,
                            get_category,
                            change_user_category,
                            log_command,
                            cancel_feedback_stat,
                            get_mailing_status,
                            check_user_category,
                            check_user_external_id
                            )
from bot.formatter import display_task
from bot.constants import LOG_COMMANDS_NAME, BOT_NAME, REASONS
from app.config import BOT_PERSISTENCE_FILE

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
# updater = Updater(token=os.getenv('TOKEN'), use_context=True)
MENU_BUTTONS = [
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


def get_subscription_button(context: CallbackContext):
    if context.user_data[SUBSCRIPTION_FLAG]:
        return InlineKeyboardButton(
            text='⏹ Остановить подписку на задания',
            callback_data='stop_subscription'
        )
    return InlineKeyboardButton(
        text='⏹ Включить подписку на задания',
        callback_data='start_subscription'
    )


@log_command(command=LOG_COMMANDS_NAME['start'], start_menu=True)
def start(update: Update, context: CallbackContext) -> int:
    deeplink_passed_param = context.args
    add_user(update.message, deeplink_passed_param)
    context.user_data[SUBSCRIPTION_FLAG] = get_mailing_status(update.effective_user.id)

    callback_data = (GREETING_REGISTERED_USER
                     if check_user_category(update.effective_user.id)
                     and check_user_external_id(update.message, deeplink_passed_param)
                     else GREETING)
    button = [
        [
            InlineKeyboardButton(text='Начнем', callback_data=callback_data)
        ]
    ]
    keyboard = InlineKeyboardMarkup(button)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Привет! 👋 \n\n'
             f'Меня зовут {BOT_NAME}. '
             'Буду держать тебя в курсе новых задач и помогу '
             'оперативно связаться с командой поддержки.',
        reply_markup=keyboard
    )
    return GREETING


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
                                 in get_category(update.effective_user.id)
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
    return CATEGORY


@log_command(command=LOG_COMMANDS_NAME['change_user_categories'])
def change_user_categories(update: Update, context: CallbackContext):
    """Auxiliary function for selecting a category and changing the status of subscriptions."""
    pattern_id = re.findall(r'\d+', update.callback_query.data)
    category_id = int(pattern_id[0])
    telegram_id = update.effective_user.id

    change_user_category(telegram_id=telegram_id, category_id=category_id)
    choose_category(update, context)
    update.callback_query.answer()


@log_command(command=LOG_COMMANDS_NAME['choose_category'],
             ignore_func=['change_user_categories'])
def choose_category(update: Update, context: CallbackContext, save_prev_msg: bool = False):
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

    user_categories = ', '.join([spec['name'] for spec
                                 in get_category(update.effective_user.id)
                                 if spec['user_selected']])

    if not user_categories:
        user_categories = 'Категории ещё не выбраны'

    update.callback_query.edit_message_text(
        text=f'Отлично! Теперь я буду присылать тебе уведомления о новых '
             f'заданиях в категориях: *{user_categories}*.\n\n'
             f'А пока можешь посмотреть открытые задания.',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=keyboard
    )
    return AFTER_CATEGORY_REPLY


@log_command(command=LOG_COMMANDS_NAME['open_menu'])
def open_menu(update: Update, context: CallbackContext):
    subscription_button = get_subscription_button(context)
    MENU_BUTTONS[-1] = [subscription_button]
    keyboard = InlineKeyboardMarkup(MENU_BUTTONS)
    text = 'Меню'
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return MENU


def open_menu_fall(update: Update, context: CallbackContext):
    subscription_button = get_subscription_button(context)
    MENU_BUTTONS[-1] = [subscription_button]
    keyboard = InlineKeyboardMarkup(MENU_BUTTONS)
    text = 'Меню'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=keyboard
    )

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

    if not context.user_data.get(START_SHOW_TASK):
        context.user_data[START_SHOW_TASK] = []

    tasks = get_user_active_tasks(
        update.effective_user.id, context.user_data[START_SHOW_TASK]
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
                    parse_mode=ParseMode.HTML
                )
                context.user_data[START_SHOW_TASK].append(task[0].id)
            else:
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=display_task(task),
                    parse_mode=ParseMode.HTML
                )
                update.callback_query.delete_message()
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text='Ты просмотрел все открытые задания на текущий момент.',
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(text='Открыть меню',
                                               callback_data='open_menu')]]
                    )
                )
                return OPEN_TASKS

        update.callback_query.delete_message()

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Есть ещё задания, показать?',
            reply_markup=keyboard
        )

    return OPEN_TASKS


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
             'опыта.\n\nИнтеллектуальный волонтёр безвозмездно дарит фонду своё '
             'время и профессиональные навыки, позволяя решать задачи, '
             'которые трудно закрыть силами штатных сотрудников.',
        reply_markup=keyboard
    )

    return MENU


@log_command(command=LOG_COMMANDS_NAME['stop_task_subscription'])
def stop_task_subscription(update: Update, context: CallbackContext):
    context.user_data[SUBSCRIPTION_FLAG] = change_subscription(update.effective_user.id)
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
        text=answer, reply_markup=cancel_feedback_keyboard
    )

    return CANCEL_FEEDBACK


@log_command(command=LOG_COMMANDS_NAME['start_task_subscription'])
def start_task_subscription(update: Update, context: CallbackContext):
    context.user_data[SUBSCRIPTION_FLAG] = change_subscription(update.effective_user.id)

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
        c['name'] for c in get_category(update.effective_user.id)
        if c['user_selected']
    ]

    answer = f'Отлично! Теперь я буду присылать тебе уведомления о ' \
             f'новых заданиях в ' \
             f'категориях: {", ".join(user_categories)}.\n\n' \
             f'А пока можешь посмотреть открытые задания.'

    update.callback_query.edit_message_text(text=answer,
                                            reply_markup=keyboard
                                            )

    return AFTER_CATEGORY_REPLY


def cancel_feedback(update: Update, context: CallbackContext):
    subscription_button = get_subscription_button(context)
    reason_canceling = update['callback_query']['data']
    telegram_id = update['callback_query']['message']['chat']['id']
    cancel_feedback_stat(telegram_id, reason_canceling)
    MENU_BUTTONS[-1] = [subscription_button]
    keyboard = InlineKeyboardMarkup(MENU_BUTTONS)
    update.callback_query.edit_message_text(
        text='Спасибо, я передал информацию команде ProCharity!',
        reply_markup=keyboard
    )

    return MENU


# @log_command(command=LOG_COMMANDS_NAME['cancel'])
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
        entry_points=[
            CommandHandler('start', start)
        ],
        states={
            GREETING: [
                CallbackQueryHandler(choose_category_after_start, pattern='^' + GREETING + '$'),
                CallbackQueryHandler(before_confirm_specializations, pattern='^' + GREETING_REGISTERED_USER + '$')
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
                CallbackQueryHandler(stop_task_subscription, pattern='^stop_subscription$'),
                CallbackQueryHandler(start_task_subscription, pattern='^start_subscription$'),
                CallbackQueryHandler(open_menu, pattern='^open_menu$')
            ],
            OPEN_TASKS: [
                CallbackQueryHandler(show_open_task, pattern='^open_task$'),
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
    updater.start_polling()
