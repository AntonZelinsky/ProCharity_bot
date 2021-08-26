import logging
import os
from logging.handlers import TimedRotatingFileHandler

from app import config

FORMATTER = u'%(asctime)s\t%(levelname)s\t%(filename)s:%(lineno)d\t%(message)s'


def create_log_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def app_logging():
    module_logger = logging.getLogger('app')
    module_logger.setLevel(logging.INFO)
    app_handler = TimedRotatingFileHandler(
        f'{config.LOG_PATH}\\app_logs',
        when="midnight",
        interval=1,
        encoding='utf-8',
        backupCount=14
    )

    formatter = logging.Formatter(FORMATTER)
    app_handler.setFormatter(formatter)
    app_loggers = [
        module_logger,
        logging.getLogger("werkzeug"),
        logging.getLogger("sqlalchemy.engine"),
        logging.getLogger("smtplib"),
    ]
    for log in app_loggers:
        log.addHandler(app_handler)
    return module_logger


def bot_logging():
    bot_logger = logging.getLogger("telegram")
    bot_logger.setLevel(logging.INFO)

    bot_handler = TimedRotatingFileHandler(
        f'{config.LOG_PATH}\\bot_logs',
        when="midnight",
        interval=1,
        encoding='utf-8',
        backupCount=14
    )
    formatter = logging.Formatter(FORMATTER)

    bot_handler.setFormatter(formatter)
    bot_logger.addHandler(bot_handler)

    app_loggers = [
        logging.getLogger("bot"),
        logging.getLogger("sqlalchemy.engine"),
        logging.getLogger("smtplib"),
    ]
    for log in app_loggers:
        log.addHandler(bot_handler)

    return bot_logger


create_log_directory(config.LOG_PATH)
app_logger = app_logging()
bot_logger = bot_logging()
logger = logging.getLogger("webhooks")
