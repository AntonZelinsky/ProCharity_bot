from flask import request, jsonify
from app.models import Task, Category
from app.database import db_session
from flask_restful import Resource
from datetime import datetime
from flask_apispec.views import MethodResource
from flask_apispec import doc, use_kwargs
from marshmallow import fields
from marshmallow.schema import Schema


class CreateCategories(MethodResource, Resource):
    @doc(description='Сreates Categories in the database',
         tags=['Create categories'])
    #@use_kwargs(CATEGORY_SCHEMA, location=('json'))
    def post(self):
        if not request.json:
            jsonify(result='is not json')
        try:
            categories = request.json
            categories_db = Category.query.filter_by(archive=False).all()
            category_id_json = [int(member['id']) for member in categories]
            category_id_db = [member.id for member in categories_db]
            category_for_adding_db = list(set(category_id_json) - set(category_id_db))
            category_for_archive = list(set(category_id_db) - set(category_id_json))
            for category in categories:
                if int(category['id']) in category_for_adding_db:
                    c = Category(
                        id=category['id'],
                        name=category['name'],
                        archive=False
                    )
                    db_session.add(c)
                
            archive_records = [category for category in categories_db if category.id in category_for_archive]
            for category in archive_records:
                category.archive = True
            db_session.commit()
            return jsonify(result='ok')            
        except:
            jsonify(result='json does not content "tasks"')