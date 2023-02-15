![develop branch CI workflow](https://github.com/ProCharity/ProCharity_bot/actions/workflows/develop_bot_ci.yml/badge.svg)
![master branch CI workflow](https://github.com/ProCharity/ProCharity_bot/actions/workflows/master_bot_ci.yml/badge.svg)

## [ProCharity_bot](https://github.com/AntonZelinsky/ProCharity_bot/) - чат-бот для рассылки заданий волонтером с сайта [procharity.ru](https://procharity.ru/) <br> [Cхема](https://miro.com/app/board/o9J_leJfeFc=/) работы бота. Ссылка на телеграм бот: [@procharity_bot](https://t.me/procharity_bot)

## Подготовка проекта
### Создать и активировать виртуальное окружение, установить зависимости:
```
python -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

### Переименовать файл .env.dev в .env и указать в нем недостающую информацию (токен бота и токен для вебхуков):
```
TOKEN=<ваш токен>
```
```
TOKEN_FOR_WEBHOOKS=<ваш токен>
```

В проекте нельзя использовать базу данных SQLite. Рекомендуется PostgreSQL.


### Создать базу и применить миграции:
```
alembic upgrade head
```

Если миграции не применились подряд, можно запустить их по очереди:
```
alembic upgrade <номер миграции>
```

В случае изменения базы создать миграции:
```
alembic revision --autogenerate -m "<описание миграции>"
```
### Запустить проект:
```
python run.py
```
### Документация API:
<http://127.0.0.1:5000/api/doc/swagger-ui/>

### Формат POST запроса для добавления категорий:
<http://127.0.0.1:5000/api/v1/categories/>
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
<http://127.0.0.1:5000/api/v1/tasks/>

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
