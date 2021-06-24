from app.models import Category


def display_task(t):
    return f'{t.title}\n\n' \
            f'От: {t.name_organization}, {t.location}\n\n' \
            f'Категория: {Category.query.filter_by(id=t.category_id).first().name}\n' \
            f'Срок: {t.deadline}\n\n{t.link}'