def display_task(t):
    return f'*{t[0].title}*\n\n' \
           f'От: {t[0].name_organization}, {t[0].location}\n\n' \
           f'Бонусы {t[0].bonus}\n' \
           f'Категория: {t[1]}\n' \
           f'Срок: {t[0].deadline}\n\n' \
           f'[Посмотреть задание]({t[0].link})'
