import logging
import os

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (Updater,
                          CommandHandler,
                          ConversationHandler,
                          CallbackContext,
                          MessageHandler,
                          Filters)

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

GREETING, CATEGORY, AFTER_CATEGORY_REPLAY, MENU, OPEN_TASKS, NO_CATEGORY, AFTER_ADD_CATEGORY, AFTER_NEW_QUESTION, AFTER_ADD_FEATURE = range(9)

category_reply_keyboard = [
    ['IT', 'Дизайн и вёрстка', 'Маректинг и коммуникация',
     'Переводы', 'Менеджмент'],
    ['Фото и видео', 'Обучение и тренинги', 'Финансы и фандрайзинг',
     'Юридический услуги', 'Стратегический консалтинг'],
    ['Готово!', 'Моих компетенций здесь нет'],
]

markup = ReplyKeyboardMarkup(category_reply_keyboard, one_time_keyboard=True)


def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Привет! Я - бот '
        'ProCharity-онлайн-платформы интеллектуального волонтёрства!'
        'Помогу тебе быть в курсе интересных задач и буду напоминать '
        'о текущих задачах.'
        'Давай начнём прямо сейчас?',
        reply_markup=ReplyKeyboardMarkup(
            [['Поехали!']], one_time_keyboard=True
        )
    )

    return GREETING


def choose_category(update: Update, context: CallbackContext):
    update.message.reply_text('Чтобы я знал, в каких задачах ты можешь '
                              'помогать фондам выбери свои профессиональные '
                              'компетенции:',
                              reply_markup=markup)
    return CATEGORY


def after_category_choose(update: Update, context: CallbackContext):
    markup = [['Посмотреть открытые задания', 'Открыть меню']]
    update.message.reply_text(
        'Ура! Теперь ты будешь получать новые задания по твоим компетенциям.'
        'А пока можешь посмотреть открытые задания.',
        reply_markup=ReplyKeyboardMarkup(markup, one_time_keyboard=True)
    )

    return AFTER_CATEGORY_REPLAY


def open_menu(update: Update, context: CallbackContext):
    markup = [['Посмотреть открытые задания', 'Задать вопрос', 'О платформе'],
              ['Изменить компетенции', 'Хочу новый функционал бота',
               'Остановить/включить подписку на задания']]
    update.message.reply_text('Меню',
                              reply_markup=ReplyKeyboardMarkup(markup, one_time_keyboard=True)
    )

    return MENU


def show_open_task(update: Update, context: CallbackContext):
    markup = [['Посмотреть ещё', 'Переслать задание другу', 'Открыть меню']]
    update.message.reply_text('ЭТО ТВОЁ ЗАДАНИЕ',
                              reply_markup=ReplyKeyboardMarkup(
                                  markup, one_time_keyboard=True
                              ))

    return OPEN_TASKS


def send_task_to_friend(update: Update, context: CallbackContext):
    pass


def ask_question(update: Update, context: CallbackContext):
    markup = [['Вернуться в меню']]
    update.message.reply_text(
        'Напишите свой вопрос',
        reply_markup=ReplyKeyboardMarkup(markup, one_time_keyboard=True)
    )

    return AFTER_NEW_QUESTION


def after_ask_question(update: Update, context: CallbackContext):
    markup = [['Посмотреть открытые задания', 'Открыть меню']]
    update.message.reply_text(
        'Спасибо, я уже передал информацию коллегам! '
        'Ответ придёт на твою почту <почта волонтёра>',
        reply_markup=ReplyKeyboardMarkup(markup, one_time_keyboard=True)
    )

    return AFTER_CATEGORY_REPLAY


def no_relevant_category(update: Update, context: CallbackContext):
    markup = [['Написать, какие компетенции добавить',
               'Посмотреть другие задания',
               'Вернуться в меню']]
    update.message.reply_text('Очень жаль!\n\nТы можешь посмотреть задания '
                              'в других категориях или поделиться с нами, '
                              'какие компетенции нам следует добавить.',
                              reply_markup=ReplyKeyboardMarkup(
                                  markup, one_time_keyboard=True
                              ))

    return NO_CATEGORY


def add_new_category(update: Update, context: CallbackContext):
    markup = [['Вернуться в меню']]
    update.message.reply_text(
        'Напиши, в какой профессиональной сфере ты бы хотел помогать',
        reply_markup=ReplyKeyboardMarkup(markup, one_time_keyboard=True)
    )

    return AFTER_ADD_CATEGORY


def after_add_new_category(update: Update, context: CallbackContext):
    markup = [['Посмотреть открытые задания', 'Открыть меню']]
    update.message.reply_text(
        'Спасибо, я уже передал информацию коллегам! '
        'Ответ придёт на твою почту <почта волонтёра>',
        reply_markup=ReplyKeyboardMarkup(markup, one_time_keyboard=True)
    )

    return AFTER_CATEGORY_REPLAY


def add_new_feature(update: Update, context: CallbackContext):
    markup = [['Вернуться в меню']]
    update.message.reply_text(
        'Напиши, какого функционала в боте тебе не хватает',
        reply_markup=ReplyKeyboardMarkup(markup, one_time_keyboard=True)
    )

    return AFTER_ADD_FEATURE


def after_add_new_feature(update: Update, context: CallbackContext):
    markup = [['Посмотреть открытые задания', 'Открыть меню']]
    update.message.reply_text(
        'Спасибо, я уже передал информацию коллегам! '
        'Ответ придёт на твою почту <почта волонтёра>',
        reply_markup=ReplyKeyboardMarkup(markup, one_time_keyboard=True)
    )

    return AFTER_CATEGORY_REPLAY


def about(update: Update, context: CallbackContext):
    markup = [['Посмотреть открытые задания', 'Задать вопрос', 'О платформе'],
              ['Изменить компетенции', 'Хочу новый функционал бота',
               'Остановить/включить подписку на задания']]
    update.message.reply_text(
        'ProCharity - это возможность для профессионалов своего дела помочь '
        'некоммерческим организациям в вопросах, которые требуют специального '
        'знания и опыта. Интеллектуальный волонтёр безвозмездно дарит фонду '
        'время и профессиональные навыки, позволяя решать задачи, которые '
        'трудно бывает закрыть силами штатных сотрудников. А фонд благодаря '
        'ему получает квалифицированную практическую помощь в решении '
        'накопившихся задач.',
        reply_markup=ReplyKeyboardMarkup(markup, one_time_keyboard=True)
    )

    return MENU


def stop_task_subscription(update: Update, context: CallbackContext):
    markup = [['Посмотреть открытые задания', 'Задать вопрос', 'О платформе'],
              ['Изменить компетенции', 'Хочу новый функционал бота',
               'Остановить/включить подписку на задания']]
    update.message.reply_text(
        'Теперь ты не будешь получать новые задания от фондов, но всегда '
        'можешь найти их на сайте http://procharity.ru',
        reply_markup=ReplyKeyboardMarkup(markup, one_time_keyboard=True)
    )

    return MENU


def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.',
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    updater = Updater(token=os.getenv('TOKEN'))
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GREETING: [MessageHandler(
                Filters.regex('^(Поехали!)$'),
                choose_category
            )],
            CATEGORY: [MessageHandler(
                Filters.regex(
                    '^(IT|Дизайн и вёрстка|Маректинг и коммуникация|'
                    'Переводы|Менеджмент|Фото и видео|Обучение и тренинги|'
                    'Финансы и фандрайзинг|Юридический услуги|'
                    'Стратегический консалтинг)$'),
                choose_category
            ),
                MessageHandler(Filters.regex('^(Готово!)$'),
                               after_category_choose),
                MessageHandler(Filters.regex('^(Моих компетенций здесь нет)$'),
                               no_relevant_category)

            ],
            AFTER_CATEGORY_REPLAY: [MessageHandler(
                Filters.regex(
                    '^Посмотреть открытые задания$'), show_open_task
                ),
                MessageHandler(Filters.regex('^Открыть меню$'), open_menu)
            ],
            MENU: [
                MessageHandler(Filters.regex('^Посмотреть открытые задания$'),
                               show_open_task),
                MessageHandler(Filters.regex('^Задать вопрос$'),
                               ask_question),
                MessageHandler(Filters.regex('^О платформе$'),
                               about),
                MessageHandler(Filters.regex('^Изменить компетенции$'),
                               choose_category),
                MessageHandler(Filters.regex('^Хочу новый функционал бота$'),
                               add_new_feature),
                MessageHandler(Filters.regex('^Остановить/включить подписку '
                                             'на задания$'),
                               stop_task_subscription)
            ],
            OPEN_TASKS: [
                MessageHandler(Filters.regex('^Посмотреть ещё$'),
                               show_open_task),
                MessageHandler(Filters.regex('^Переслать задание другу$'),
                               send_task_to_friend),
                MessageHandler(Filters.regex('^Открыть меню$'),
                               open_menu)
            ],
            NO_CATEGORY: [
                MessageHandler(Filters.regex('^Написать, какие компетенции '
                                             'добавить$'),
                               add_new_category),
                MessageHandler(Filters.regex('^Посмотреть другие задания$'),
                               show_open_task),
                MessageHandler(Filters.regex('^Вернуться в меню$'),
                               open_menu),
            ],
            AFTER_ADD_CATEGORY: [
                MessageHandler(Filters.text, after_add_new_category)
            ],
            AFTER_NEW_QUESTION: [
                MessageHandler(Filters.text, after_ask_question)
            ],
            AFTER_ADD_FEATURE: [
                MessageHandler(Filters.text, after_add_new_feature)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()
