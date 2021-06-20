from datetime import datetime
from app.models import User, Statistics
from app.database import db_session
from datetime import datetime


def statistics(telegram_id, command):
    try:
        user_id = User.query.filter_by(
            telegram_id=int(telegram_id),
        ).first().id
        statistics = Statistics(user_id=user_id,
                                command=command,
                                write_date=datetime.today().date())
        db_session.add(statistics)
        db_session.commit()
    except:
        return 'error write in db'


def analysis(bid, telegram_id):
    pass
