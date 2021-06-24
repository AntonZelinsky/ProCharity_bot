def display_task(t):
    return f'{t.title}\n\n' \
            f'От {t.name_organization}, {t.location}\n\n' \
            f'Категория {t.name_organization}\n' \
            f'Срок: {t.deadline}\n\n{t.link}'