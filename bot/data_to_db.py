from app.models import ReasonCanceling, User, Category, Task, Statistics, Users_Categories, ExternalSiteUser
from app.database import db_session
from datetime import datetime
from sqlalchemy.orm import load_only
from sqlalchemy import select
import inspect


def add_user(message):
    telegram_id = message.chat.id
    last_name, first_name, username = message.chat.last_name, message.chat.first_name, message.chat.username
    user = User.query.filter_by(telegram_id=telegram_id).first()

    if not user:
        user = User(
            telegram_id=telegram_id,
            last_name=last_name,
            first_name=first_name,
            username=username,
            date_registration=datetime.now(),
        )
        db_session.add(user)
        return db_session.commit()

    record_updated = False

    if not user.external_id:
        if user.last_name != last_name:
            user.last_name = last_name
            record_updated = True

        if user.first_name != first_name:
            user.first_name = first_name
            record_updated = True

    if user.username != username:
        user.username = username
        record_updated = True

    if record_updated:
        return db_session.commit()


def external_user_registering(external_id_hash, message):
    external_user = ExternalSiteUser.query.filter_by(external_id_hash=external_id_hash).first()

    if not external_user:
        return False

    user = User.query.filter_by(telegram_id=message.chat.id).first()

    user.first_name = external_user.first_name
    user.last_name = external_user.last_name
    user.external_id = external_user.external_id
    user.email = external_user.email

    if external_user.specializations:
        external_user_specializations = [int(x) for x in external_user.specializations.split(',')]
        specializations = Category.query.filter(Category.id.in_(external_user_specializations)).all()
        for specialization in specializations:
            user.categories.append(specialization)
    db_session.add(user)
    db_session.commit()


def check_user_category(telegram_id):
    user_categories = User.query.get(telegram_id).categories
    if not user_categories:
        return False
    return True


def get_category(telegram_id):
    """
    Returns a collection of categories. If the user has selected one of them, it returns True in dictionary.
    :param telegram_id: chat_id of current user
    :return:
    """
    result = []
    user_categories = [cat.id for cat in User.query.filter_by(telegram_id=telegram_id).first().categories]
    all_categories = Category.query.options(load_only('id')).filter_by(archive=False)
    for category in all_categories:
        cat = {}
        cat['category_id'] = category.id
        cat['name'] = category.name
        if category.id in user_categories:
            cat['user_selected'] = True
        else:
            cat['user_selected'] = False
        result.append(cat)
    return result


def get_task():
    return Task.query.limit(3).all()


def get_user_active_tasks(telegram_id, shown_task):
    stmt = select(Task, Category.name). \
        where(Users_Categories.telegram_id == telegram_id). \
        where(Task.archive == False).where(~Task.id.in_(shown_task)). \
        join(Users_Categories, Users_Categories.category_id == Task.category_id). \
        join(Category, Category.id == Users_Categories.category_id)

    result = db_session.execute(stmt)
    return [[task, category_name] for task, category_name in result]


def get_mailing_status(telegram_id):
    user = User.query.options(load_only('has_mailing')).filter_by(telegram_id=telegram_id).first()
    return user.has_mailing


def change_subscription(telegram_id):
    """
    Update subscription status of user.
    :param telegram_id: Chat id of current user from the telegram update obj.
    :return:
    """
    user = User.query.options(load_only('has_mailing')).filter_by(telegram_id=telegram_id).first()

    if user.has_mailing:
        user.has_mailing = False
    else:
        user.has_mailing = True
    db_session.commit()

    return user.has_mailing


def log_command(command, start_menu=False, ignore_func=None, ):
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
                if code_obj_name == ignore_func:
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


def change_user_category(telegram_id, category_id):
    user = User.query.filter_by(telegram_id=telegram_id).first()
    category = Category.query.get(category_id)

    if category in user.categories:
        user.categories.remove(category)
        db_session.add(user)
    else:
        user.categories.append(category)
        db_session.add(user)
    db_session.commit()


def cancel_feedback_stat(telegram_id, reason_canceling):
    # reason_canceling = update['callback_query']['data']
    # telegram_id = update['callback_query']['message']['chat']['id']
    reason = ReasonCanceling(
        telegram_id=telegram_id,
        reason_canceling=reason_canceling
    )
    db_session.add(reason)
    return db_session.commit()
