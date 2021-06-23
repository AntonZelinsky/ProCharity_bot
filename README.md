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

### Формат POST запроса для добавления категорий:
-<http://127.0.0.1:5000/api/webhook/categories/>
```json
[
   {
      "id":"1",
      "name":"Дизайн и верстка"
   },
   {
      "id":"2",
      "name":"Маркетинг и коммуникации"
   }
]
```
### Формат POST запроса для добавления заданий:
-<http://127.0.0.1:5000/api/webhook/tasks/>

```json
[
  {
      "id":"32539",
      "title":"Создание семантического ядра",
      "name_organization":"фонд СеллСтандарт",
      "deadline":"25.06.2021",
      "category":"Маркетинг и коммуникации",
      "category_id":"2",
      "bonus":"4",
      "location":"Санкт-Петербург",
      "link":"https://procharity.ru/tasks/detail.php?ID=32539",
      "description":""
   },
   {
      "id":"33098",
      "title":"Видеосъемка фильма о проекте",
      "name_organization":"БФ «Гольфстрим»",
      "deadline":"21.06.2021",
      "category":"Фото и видео",
      "category_id":"12",
      "bonus":"5",
      "location":"Москва",
      "link":"https://procharity.ru/tasks/detail.php?ID=33098",
      "description":""
   }
]
```
