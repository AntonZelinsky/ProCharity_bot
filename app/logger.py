import logging
import os
from logging.handlers import TimedRotatingFileHandler

from app import config

FORMATTER = u'%(asctime)s\t%(levelname)s\t%(filename)s:%(lineno)d\t%(message)s'


def create_log_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def set_logger(logger, level, path_name, loggers=None):
    logger.setLevel(level)
    logger_handler = TimedRotatingFileHandler(
        f'{config.LOG_PATH}\\{path_name}',
        when="midnight",
        interval=1,
        encoding='utf-8',
        backupCount=14
    )
    formatter = logging.Formatter(FORMATTER)
    logger_handler.setFormatter(formatter)
    if loggers:
        for log in loggers:
            log.addHandler(logger_handler)
    logger.addHandler(logger_handler)
    return logger


logger_for_app = logging.getLogger('app')
app_loggers = [
        logger_for_app,
        logging.getLogger("werkzeug"),
        logging.getLogger("sqlalchemy.engine"),
        logging.getLogger("smtplib"),
    ]

logger_for_bot = logging.getLogger("telegram")
bot_loggers = [
        logging.getLogger("bot"),
        logging.getLogger("sqlalchemy.engine"),
        logging.getLogger("smtplib"),
    ]

webhooks_logger = logging.getLogger("webhooks")


create_log_directory(config.LOG_PATH)
app_logger = set_logger(logger_for_app, logging.INFO, 'app_logs', app_loggers)
bot_logger = set_logger(logger_for_bot, logging.INFO, 'bot_logs', bot_loggers)
webhooks_logger = set_logger(webhooks_logger, logging.INFO, 'webhooks_logs')
