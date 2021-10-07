from flask import request, jsonify, make_response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import load_only
from app.models import Category
from app.database import db_session
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import doc

from app.logger import webhooks_logger as logger
from app.apis.check_webhooks_token import check_webhooks_token


class CreateCategories(MethodResource, Resource):
    method_decorators = {'post': [check_webhooks_token]}
    @doc(description='Сreates Categories in the database',
         tags=['Create categories'],
         params={'token': {
             'description': 'webhooks token',
             'in': 'header',
             'type': 'string',
             'required': True
         }})
    def post(self):
        if not request.json:
            logger.error('Categories: The request has no data in passed json.')
            return make_response(jsonify(result='Json contains no data '), 400)

        categories = request.json
        categories_db = Category.query.options(load_only('archive')).all()
        category_id_json = [int(member['id']) for member in categories]
        category_id_db = [member.id for member in categories_db]
        category_id_db_not_archive = [member.id for member in categories_db if member.archive == False]
        category_id_db_archive = list(
            set(category_id_db) - set(category_id_db_not_archive)
        )
        category_for_unarchive = list(
            set(category_id_db_archive) & set(category_id_json)
        )
        category_for_adding_db = list(set(category_id_json) - set(category_id_db))
        category_for_archive = list(set(category_id_db_not_archive) - set(category_id_json))
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
        unarchive_records = [category for category in categories_db if category.id in category_for_unarchive]
        for task in unarchive_records:
            task.archive = False

        try:
            db_session.commit()
        except SQLAlchemyError as ex:
            logger.error(f'Categories: Database commit error "{str(ex)}"')
            db_session.rollback()
            return make_response(jsonify(message=f"Bad request: {str(ex)}"), 400)

        logger.info("Categories: New categories successfully added.")
        return make_response(jsonify(result='ok'), 200)
