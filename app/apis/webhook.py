from flask import request, jsonify
from app.models import Task, Category
from app.database import db_session
from flask_restful import Resource
from datetime import datetime
from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs
from marshmallow import fields
from marshmallow.schema import Schema

{'message': fields.Str()}

class TaskSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    name_organization = fields.Str()
    deadline = fields.Str()
    category_id = fields.Str(),
    bonus = fields.Str()
    location = fields.Str()
    link = fields.Str()
    description = fields.Str()


TASKS_SCHEMA = {"tasks": fields.List(
    fields.Nested(TaskSchema())
)}


class Create_tasks(MethodResource, Resource):
    @doc(description='Сreates tasks in the database',
         tags=['Create tasks'])
    #@use_kwargs(TASKS_SCHEMA, location=('json'))
    def post(self):
        if not request.json:
            jsonify(result='is not json')
        try:
            tasks = request.json['tasks']
            tasks_db = Task.query.filter_by(archive=False).all()
            task_id_json = [int(member['id']) for member in tasks]
            task_id_db = [member.id for member in tasks_db]
            task_for_adding_db = list(set(task_id_json) - set(task_id_db))
            task_for_archive = list(set(task_id_db) - set(task_id_json))
            for task in tasks:
                if int(task['id']) in task_for_adding_db:
                    t = Task(
                        id=task['id'],
                        title=task['title'],
                        name_organization=task['name_organization'],
                        deadline=datetime.strptime(
                            task['deadline'], '%d.%m.%Y'
                        ).date(),
                        category_id=task['category_id'],
                        bonus=task['bonus'],
                        location=task['location'],
                        link=task['link'],
                        description=task['description'],
                        archive=False
                    )
                    db_session.add(t)
            archive_records = [task for task in tasks_db if task.id in task_for_archive]
            for task in archive_records:
                task.archive = True
            db_session.commit()
            return jsonify(result='ok')
        except:
            jsonify(result='json does not content "tasks"')


class Create_categories(MethodResource, Resource):
    @doc(description='Сreates Categories in the database',
         tags=['Create categories'])
    #@use_kwargs(CATEGORY_SCHEMA, location=('json'))
    def post(self):
        if not request.json:
            jsonify(result='is not json')
        try:
            print('OK')
            categories = request.json['categories']
            print(2222)
            categories_db = Category.query.filter_by(archive=False).all()
            print(333)
            category_id_json = [int(member['id']) for member in categories]
            category_id_db = [member.id for member in categories_db]
            category_for_adding_db = list(set(category_id_json) - set(category_id_db))
            category_for_archive = list(set(category_id_db) - set(category_id_json))
            for category in categories:
                print(category)
                if int(category['id']) in category_for_adding_db:
                    c = Category(
                        id=category['id'],
                        name=category['name'],
                        archive=False
                    )
                    print(c)
                    db_session.add(c)
                
            archive_records = [category for category in categories_db if category.id in category_for_archive]
            for category in archive_records:
                category.archive = True
            db_session.commit()
            return jsonify(result='ok')            
        except:
            jsonify(result='json does not content "tasks"')
