![example workflow](https://github.com/kr0t/ProCharrity_bot/actions/workflows/develop_bot_ci.yml/badge.svg)
![example workflow](https://github.com/kr0t/ProCharrity_bot/actions/workflows/master_bot_ci.yml/badge.svg)

## [ProCharity_bot](https://github.com/AntonZelinsky/ProCharrity_bot/) - чат-бот для рассылки заданий волонтером с сайта [procharity.ru](https://procharity.ru/) <br> [Cхема](https://miro.com/app/board/o9J_leJfeFc=/) работы бота. [Бот](https://t.me/procharity_bot) в телеграм.

## Подготовка проекта
### Создать и активировать виртуальное окружение, установить зависимости:
```
python -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```
### Переименовать файл .env.dev в .env и указать в нем недостающую информацию (используемую базу данных и токен бота):
```
DATABASE_URL=postgres://{user}:{password}@{hostname}:{port}/{database-name}
TOKEN=<ваш токен>
```
### Создать базу и применить миграции:
```
alembic upgrade head
```
В случае изменения базы создать миграции:
```
alembic revision --autogenerate -m "<описание миграции>"
```
### Запустить проект:
```
flask run
```
### Документация API:
<http://127.0.0.1:5000/api/doc/swagger-ui/>

### Формат POST запроса для добавления категорий:
<http://127.0.0.1:5000/api/webhook/categories/>
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
<http://127.0.0.1:5000/api/webhook/tasks/>

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
