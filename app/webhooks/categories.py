from flask import request
from flask_apispec import doc
from flask_apispec.views import MethodResource
from flask_restful import Resource

from app.database import db_session
from app.models import Category
from app.request_models.category import CategoryCreateRequest
from app.webhooks.check_request import request_to_context
from app.webhooks.check_webhooks_token import check_webhooks_token
from core.repositories.category_repository import CategoryRepository


category_repository = CategoryRepository(db_session)


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
        categories = request_to_context(CategoryCreateRequest, request)
        categories_dict = {category.id: category for category in categories}

        categories_db = category_repository.get_all_categories()

        category_id_json = [member.id for member in categories]
        category_id_db = [member.id for member in categories_db]

        category_id_db_not_archive = [member.id for member in categories_db if member.archive is False]
        category_id_db_archive = list(set(category_id_db) - set(category_id_db_not_archive))

        category_for_unarchive = list(set(category_id_db_archive) & set(category_id_json))
        category_for_adding_db = list(set(category_id_json) - set(category_id_db))
        category_for_archive = list(set(category_id_db_not_archive) - set(category_id_json))

        categories_for_add = []

        for category in categories:
            if category.id in category_for_adding_db:
                c = Category(
                    id=category.id,
                    name=category.name,
                    archive=False,
                    parent_id=category.parent_id
                )
                categories_for_add.append(c)

        archive_records = [category for category in categories_db if category.id in category_for_archive]
        for category in archive_records:
            category.archive = True
        unarchive_records = [category for category in categories_db if category.id in category_for_unarchive]

        categories_for_update = list(
            set(category_id_json) - set(category_for_archive) - set(category_for_adding_db))

        active_category = [category for category in categories_db if category.id in categories_for_update]

        if active_category:
            self.__update_active_category(active_category, categories_dict)

        for task in unarchive_records:
            task.archive = False

        return category_repository.update_categories(categories_for_add)

    def __hash__(self, category):
        if type(category) == dict:
            id = category.get('id')
            name = category.get('name')
            parent_id = category.get('parent_id')
            return hash(f'{id}{name}{parent_id}')
        return hash(f'{category.id}{category.name}{category.parent_id}')

    def __update_active_category(self, active_category, categories):
        for category in active_category:
            category_from_dict = categories.get(category.id)
            if self.__hash__(category) != self.__hash__(category_from_dict):
                self.__update_category_fields(category, category_from_dict)

    def __update_category_fields(self, category, category_from_dict):
        category.name = category_from_dict.name
        category.parent_id = category_from_dict.parent_id
        category.archive = False
