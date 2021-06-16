## Первоначальная подготовка проекта

### Необходимо создать виртуальное окружение и установить все зависимости:
- python -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt

### Создать файл .env и указать в нем используемую базу. Тестовая: 
- DATABASE_URL=sqlite:///db.db

### Создать базу и применить миграции:
- alembic upgrade head
### Для информации:
- Создание новой миграции в случае изменения базы: alembic revision --autogenerate -m "message"
