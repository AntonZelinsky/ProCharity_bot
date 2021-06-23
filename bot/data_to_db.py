from app.models import User
from app.database import db_session


def add_user(message):
    telegram_id = message.chat.id
    last_name, first_name = message.chat.last_name, message.chat.first_name
    record = User.query.filter_by(telegram_id=telegram_id).first()
    if not record:
        record = User(telegram_id=telegram_id)
        record.last_name = last_name
        record.first_name = first_name
        db_session.add(record)
        db_session.commit()
        return
    if (record.last_name != last_name) or (record.first_name != first_name):
        record.last_name = last_name
        record.first_name = first_name
        db_session.commit()
    return
