import locale
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

def display_task(t):
    return f'<b>{t[0].title}</b>\n\n' \
           f'От {t[0].name_organization}, {t[0].location}\n\n' \
           f'Бонусы {"💎" * t[0].bonus}\n' \
           f'Категория: {t[1]}\n' \
           f'Срок: {t[0].deadline.strftime("%d %B %Y")}г.\n\n' \
           f'<u><a href="{t[0].link}">Посмотреть задание</a></u>'


def display_task_notification(task):
    return (f'<b>{task.title}</b>\n\n'
            f'От {task.name_organization}, {task.location}\n\n'
            f'Бонусы {"💎" * task.bonus}\n'
            f'Категория: {task.categories.name}\n'
            f'Срок: {task.deadline.strftime("%d %B %Y")}г.\n\n'
            f'<u><a href="{task.link}">Посмотреть задание</a></u>')

