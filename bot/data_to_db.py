from app.models import User, Category, Task
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


def get_category():
    categories = Category.query.all()
    return [category.name for category in categories]


def get_task():
    return Task.query.limit(3).all()


def display_task(t):
    return f'{t.title}\n\n' \
           f'От {t.name_organization}, {t.location}\n\n' \
           f'Категория {t.name_organization}\n' \
           f'Срок: {t.deadline}\n\n{t.link}'


def change_subscription(chat_id):
    """
    Update subscription status of user
    :param chat_id: Chat id of current user from the telegram update obj.
    :return:
    """
    user = User.query.filter_by(telegram_id=chat_id).first()

    if user.has_mailing:
        user.has_mailing = False
    else:
        user.has_mailing = True
    db_session.commit()

    return user.has_mailing
