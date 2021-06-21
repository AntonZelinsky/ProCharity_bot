from datetime import datetime
from app.models import User, Statistics
from app.database import db_session
from datetime import datetime


def add_comand(telegram_id, command):
    try:
        statistics = Statistics(telegram_id=telegram_id,
                                command=command,
                                added_date=datetime.today().date())
        db_session.add(statistics)
        db_session.commit()
    except:
        return 'error write in db'


def analysis(bid, telegram_id):
    pass
