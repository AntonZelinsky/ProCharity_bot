from flask import jsonify, make_response
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import load_only, Session

from typing import Optional

from app.logger import webhooks_logger as logger
from app.models import Category
from core.repositories.abstract_repository import AbstractRepository


class CategoryRepository(AbstractRepository):

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_or_none(self, category_id: int) -> Optional[Category]:
        return self.session.get(Category, category_id)

    def get(self, category_id: int) -> Category:
        category = self.get_or_none(category_id)
        if not category:
            raise LookupError(f'Category ID={category_id} not found')
        return category

    def get_all_categories(self) -> list[Category]:
        categories = Category.query.options(load_only('archive')).all()
        return categories

    def create(self, category: Category) -> Category:
        self.session.add(category)
        try:
            self.session.commit()
        except SQLAlchemyError as ex:
            logger.error(f'Add New Category: Database commit error "{str(ex)}"')
            self.session.rollback()
            return make_response(jsonify(message=f'Bad request: {str(ex)}'), 400)
        logger.info('Add New Category: New categories successfully added.')
        return category

    def update_categories(self, categories: list[Category]) -> str:
        self.session.add_all(categories)
        try:
            self.session.commit()
        except SQLAlchemyError as ex:
            logger.error(f'Categories: Database commit error "{str(ex)}"')
            self.session.rollback()
            return make_response(jsonify(message=f'Bad request: {str(ex)}'), 400)
        logger.info('Categories: New categories successfully added.')
        return make_response(jsonify(result='ok'), 200)

    def update(self, category: Category) -> Category:
        self.session.refresh(category)
        self.session.commit()
        return category
