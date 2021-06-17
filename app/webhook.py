from flask import request, jsonify
from app.models import Task, Category
from app.database import db_session
from flask_restful import Resource
from datetime import datetime


class Create_tasks(Resource):
    def post(self):
        if not request.json:
            jsonify(result='is not json')
        try:
            tasks = request.json['tasks']
            tasks_db = Task.query.all()
            tasks_query_id = []
            for task in tasks:
                print(task)
                record = Task.query.filter(
                    Task.task_api_id == task['id']
                ).first()
                if not record:
                    t = Task(
                        task_api_id=task['id'],
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
                    db_session.commit()
                tasks_query_id.append(int(task['id']))
            print(tasks_query_id)
            for task in tasks_db:
                print(f'Значение {task.task_api_id}')
                if not (task.task_api_id in tasks_query_id) and (
                    not task.archive
                ):
                    task.archive = True
                    db_session.commit()
            return jsonify(result='ok')
        except:
            jsonify(result='json does not content "tasks"')


class Create_categories(Resource):
    def post(self):
        if not request.json:
            jsonify(result='is not json')
        try:
            categories = request.json['categories']
            #categories_db = Category.query.all()
            category_query_id = []
            for category in categories:
                record = Category.query.filter(Category.category_api_id == category['id']).first()
                if not record:
                    c = Category(
                        category_api_id=category['id'],
                        name=category['name'],
                        archive=False
                    )
                    db_session.add(c)
                    db_session.commit()
                category_query_id.append(category['id'])
            
            return jsonify(result='ok')
        except:
            jsonify(result='json does not content "tasks"')
