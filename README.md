## Первоначальная подготовка проекта

### Необходимо создать виртуальное окружение и установить все зависимости:
- python -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt

### Создать файл .env и указать в нем
- Используемую базу. Тестовая:
  
`DATABASE_URL=sqlite:///db.db`

- токен бота:
`TOKEN=<TOKEN_BOT>`

### Создать базу и применить миграции:
- alembic upgrade head
### Для информации:
- Создание новой миграции в случае изменения базы: alembic revision --autogenerate -m "message"

### Документация API:
- <http://127.0.0.1:5000/api/doc/swagger-ui/>

