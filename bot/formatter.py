def display_task(t):
    return f'*{t[0].title}*\n\n' \
           f'От: {t[0].name_organization}, {t[0].location}\n\n' \
           f'Бонусы {t[0].bonus}\n' \
           f'Категория: {t[1]}\n' \
           f'Срок: {t[0].deadline}\n\n' \
           f'[Посмотреть задание]({t[0].link})'


def display_task_notification(task):
    return (f'<b>{task.title}</b>\n\n'
            f'От: {task.name_organization}, {task.location}\n\n'
            f'Бонусы {"💎" * task.bonus}\n'
            f'Категория: {task.categories.name}\n'
            f'Срок: {task.deadline}\n\n'
            f'<a href="{task.link}">Посмотреть задание</a>')