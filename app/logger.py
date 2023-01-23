import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

import pytz

from app import config

logging.Formatter.converter = lambda *args: datetime.now(tz=pytz.timezone('Europe/Minsk')).timetuple()

FORMATTER = f'%(asctime)s\t%(levelname)s\t%(filename)s:%(lineno)d\t%(message)s'


def create_log_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def add_handler(path_name):
    handler = TimedRotatingFileHandler(
        f'{config.LOG_PATH}/{path_name}',
        when="midnight",
        interval=1,
        encoding='utf-8',
        backupCount=14
    )
    formatter = logging.Formatter(FORMATTER)
    handler.setFormatter(formatter)
    return handler


def app_logging():
    module_logger = logging.getLogger('app')
    module_logger.setLevel(logging.INFO)
    app_handler = add_handler('app_logs.txt')
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
    bot_handler = add_handler('bot_logs.txt')
    bot_logger.addHandler(bot_handler)
    app_loggers = [
        logging.getLogger("bot"),
        logging.getLogger("sqlalchemy.engine"),
        logging.getLogger("smtplib"),
    ]
    for log in app_loggers:
        log.addHandler(bot_handler)

    return bot_logger


def webhooks_logging():
    webhooks_logger = logging.getLogger("webhooks")
    webhooks_logger.setLevel(logging.INFO)
    webhooks_handler = add_handler('webhooks_logs.txt')
    webhooks_logger.addHandler(webhooks_handler)

    return webhooks_logger


create_log_directory(config.LOG_PATH)
app_logger = app_logging()
bot_logger = bot_logging()
webhooks_logger = webhooks_logging()
