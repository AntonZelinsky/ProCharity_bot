import logging
import os
from logging.handlers import RotatingFileHandler
from app import config

FORMATTER = '%(asctime)s  %(levelname)s : %(message)s \n[in  %(pathname)s : %(lineno)d ]\n'


def create_log_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def app_logging():
    module_logger = logging.getLogger('app')
    module_logger.setLevel(logging.INFO)

    app_handler = RotatingFileHandler(
        f'{config.LOG_PATH}\\app_logs.log',
        encoding='utf-8',
        maxBytes=500000,
        backupCount=10
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

    bot_handler = RotatingFileHandler(
        f'{config.LOG_PATH}\\bot_logs.log',
        encoding='utf-8',
        maxBytes=500000,
        backupCount=10
    )
    formatter = logging.Formatter(FORMATTER)

    bot_handler.setFormatter(formatter)
    bot_logger.addHandler(bot_handler)
    return bot_logger


create_log_directory(config.LOG_PATH)
app_logger = app_logging()
bot_logger = bot_logging()
