import inspect
import logging

from app.models import Statistics
from app.database import db_session
from datetime import datetime


def log_command(command, ignore_func: list = None):
    def log(func):
        def wrapper(*args, **kwargs):            
            try:
                update = args[0]
                if ignore_func:
                    current_frame = inspect.currentframe()
                    caller_frame = current_frame.f_back
                    code_obj = caller_frame.f_code
                    code_obj_name = code_obj.co_name

                    if code_obj_name in ignore_func:
                        return func(*args, **kwargs)

                statistic = Statistics(telegram_id=update.effective_user.id,
                                       command=command,
                                       added_date=datetime.now())

                db_session.add(statistic)
                db_session.commit()

                return func(*args, **kwargs)
            except Exception as e:
                logging.getLogger(__name__).error(f"Ошибка {e} после команды '{ command }'")
        return wrapper

    return log