from app.database import db_session
from app.models import Category, Task


def get_category():
    categories = db_session.query(Category).all()
    return [category.name for category in categories]


def get_task():
    return db_session.query(Task).limit(3).all()


def display_task(t):
    return f'{t.title}\n\n' \
            f'От {t.name_organization}, {t.location}\n\n' \
            f'Категория {t.name_organization}\n' \
            f'Срок: {t.deadline}\n\n{t.link}'
