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


def get_category():
    categories = Category.query.all()
    return [category.name for category in categories]


def get_task():
    return Task.query.limit(3).all()


def get_tasks(telegram_id):
    categories = User.query.filter_by(
        telegram_id=int(telegram_id)
    ).first().categories
    tasks = []
    for category in categories:
        for task in category.tasks:
            if not task.archive:
                task_lst = [task, Category.query.filter_by(id=task.category_id).first().name]
                tasks.append(task_lst)
    return tasks


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


def log_command(telegram_id, command):
    """
    Add information of using bot commands to DB.

    :param chat_id: Chat id of current user from the telegram update obj.
    :param command: The command clicked in the telegram chat by current user.
    :return:
    """
    statistic = Statistics(telegram_id=telegram_id,
                           command=command,
                           added_date=datetime.now())

    db_session.add(statistic)
    db_session.commit()


def change_user_category(telegram_id, category):
    user = User.query.filter_by(telegram_id=int(telegram_id)).first()
    category = Category.query.filter_by(name=category).first()
    categories_list = user.categories
    if category in categories_list:
        user.categories.remove(category)
        db_session.add(user)
        db_session.commit()
        return False
    user.categories.append(category)
    db_session.add(user)
    db_session.commit()
    return True
