## Первоначальная подготовка проекта

### Необходимо создать виртуальное окружение и установить все зависимости:
- python -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt

### Создать файл .env и указать в нем:

#### 1. Используемую базу. 
(Для разработки можно указать) 

`DATABASE_URL=sqlite:///db.db`

#### 2. Токен для бота:

`TOKEN=<TOKEN_BOT>`


### Создать базу и применить миграции:
- alembic upgrade head
### Для информации:
- Создание новой миграции в случае изменения базы: alembic revision --autogenerate -m "message"
