from app.models import Statistics
from app.database import db_session
from datetime import datetime

import inspect


def log_command(command, start_menu=False, ignore_func: list = None):
    """
    Add information of using bot commands to DB.
    :param command: Commands passed to the bot for adding to the database
    :param start_menu: It should be set True if the first call to the bot
     is being made and the callback is not used to get the response data.
    :param ignore_func: Ignoring logging based on the name of the called function.
    :return:
    """

    def log(func):
        def wrapper(*args, **kwargs):

            if ignore_func:
                current_frame = inspect.currentframe()
                caller_frame = current_frame.f_back
                code_obj = caller_frame.f_code
                code_obj_name = code_obj.co_name
                if code_obj_name in ignore_func:
                    return func(*args, **kwargs)

            if start_menu:
                telegram_id = args[0].message.chat.id
            else:
                telegram_id = args[0].callback_query.message.chat.id

            statistic = Statistics(telegram_id=telegram_id,
                                   command=command,
                                   added_date=datetime.now())

            db_session.add(statistic)
            db_session.commit()
            return func(*args, **kwargs)

        return wrapper

    return log
