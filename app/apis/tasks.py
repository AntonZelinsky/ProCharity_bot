from datetime import datetime

from flask import request, jsonify, make_response
from flask_apispec import doc
from flask_apispec.views import MethodResource
from flask_restful import Resource
from sqlalchemy import exc
from sqlalchemy.orm import load_only

from app.database import db_session
from app.models import Task, User
from bot.formatter import display_task_notification
from bot.messages import TelegramNotification

# class Task_schema(Schema):
#     id = fields.Int()
#     title = fields.Str()
#     name_organization = fields.Str()
#     deadline = fields.Str()
#     category_id = fields.Str(),
#     bonus = fields.Str()
#     location = fields.Str()
#     link = fields.Str()
#     description = fields.Str()


# TASKS_SCHEMA =  fields.List(
#     fields.Nested(Task_schema())
# )


class CreateTasks(MethodResource, Resource):
    @doc(description='Сreates tasks in the database',
         tags=['Create tasks'],
         responses={
             200: {'description': 'ok'},
             400: {'description': 'error message'},
         },
         )
    # @use_kwargs(Task_schema, location=('json'))
    def post(self):
        if not request.json:
            return make_response(jsonify(result='the request cannot be empty'), 400)

        tasks = request.json
        tasks_db = Task.query.options(load_only('archive')).all()
        task_id_json = [int(task['id']) for task in tasks]
        task_id_db = [task.id for task in tasks_db]
        task_id_db_not_archive = [task.id for task in tasks_db if task.archive == False]
        task_id_db_archive = list(
            set(task_id_db) - set(task_id_db_not_archive)
        )
        task_for_unarchive = list(
            set(task_id_db_archive) & set(task_id_json)
        )
        task_for_adding_db = list(
            set(task_id_json) - set(task_id_db)
        )
        task_for_archive = list(
            set(task_id_db_not_archive) - set(task_id_json)
        )
        task_to_send = []

        for task in tasks:
            if int(task['id']) in task_for_adding_db:
                task['deadline'] = datetime.strptime(task['deadline'], '%d.%m.%Y').date()
                task['archive'] = False
                del task['category']

                new_task = Task(**task)
                db_session.add(new_task)
                task_to_send.append(new_task)

        archive_records = [task for task in tasks_db if task.id in task_for_archive]

        for task in archive_records:
            task.archive = True
            task.updated_date = datetime.now()

        unarchive_records = [task for task in tasks_db if task.id in task_for_unarchive]

        try:
            for task in tasks:
                for unarchive_task in unarchive_records:
                    if unarchive_task.id == int(task['id']):
                        del task['category']
                        task['archive'] = False
                        task['updated_date'] = datetime.now()
                        Task.query.filter_by(id=int(unarchive_task.id)).update(task)

            db_session.commit()
            self.send_task(task_to_send)

        except exc.SQLAlchemyError as ex:
            db_session.rollback()
            return make_response(jsonify(result=f'request error {str(ex)}'), 400)

        return make_response(jsonify(result='ok'), 200)

    def send_task(self, task_to_send):
        if task_to_send:
            users = User.query.options(load_only('telegram_id')).filter_by(has_mailing=True).all()
            notification = TelegramNotification()

            for task in task_to_send:
                chats_list = []
                for user in users:
                    if task.category_id in [cat.id for cat in user.categories]:
                        chats_list.append(user)

                if chats_list:
                    notification.send_new_tasks(message=display_task_notification(task), send_to=chats_list)
