from app.models import User, Category, Task, Statistics
from app.database import db_session
from datetime import datetime


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


def log_command(telegram_id, command):
    try:
        if not telegram_id.isdigit():
            return 'telegram_id consists not number'
        statistics = Statistics(telegram_id=telegram_id,
                                command=command,
                                added_date=datetime.today().date())
        db_session.add(statistics)
        db_session.commit()
    except:
        return 'error write in db'


def get_category():
    categories = Category.query.all()
    return [category.name for category in categories]


def get_task():
    return Task.query.limit(3).all()


def display_task(t):
    return f'{t.title}\n\n' \
            f'От: {t.name_organization}, {t.location}\n\n' \
            f'Категория: {Category.query.filter_by(id=t.category_id).first().name}\n' \
            f'Срок: {t.deadline}\n\n{t.link}'


def get_tasks(telegram_id):
    categories = User.query.filter_by(
        telegram_id=telegram_id
    ).first().categories
    tasks = []
    for category in categories:
        for task in category.task:
            if not task.archive:
                tasks.append(task)
    return tasks
