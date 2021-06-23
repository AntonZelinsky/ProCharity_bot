from app.models import Category, Task


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
