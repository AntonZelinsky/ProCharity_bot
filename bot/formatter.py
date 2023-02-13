import locale
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

UTM_STAMP = '&utm_source=telegram' \
            '&utm_medium=social' \
            '&utm_campaign=bot_procharity'


def display_task(t):
    return f'<b>{t[0].title}</b>\n\n' \
           f'От {t[0].name_organization}{", " + str(t[0].location) if t[0].location else ""}\n\n' \
           f'Бонусы {"💎" * t[0].bonus}\n' \
           f'Категория: {t[1]}\n' \
           f'Срок: {t[0].deadline.strftime("%d %B %Y").lstrip("0")}г.\n\n' \
           f'<u><a href="{t[0].link}{UTM_STAMP}">Посмотреть задание</a></u>'


def display_task_notification(task):
    return (f'<b>{task.title}</b>\n\n'
            f'От {task.name_organization}{", " + str(task.location) if task.location else ""}\n\n'
            f'Бонусы {"💎" * task.bonus}\n'
            f'Категория: {task.categories.name}\n'
            f'Срок: {task.deadline.strftime("%d %B %Y").lstrip("0")}г.\n\n'
            f'<u><a href="{task.link}{UTM_STAMP}">Посмотреть задание</a></u>')
