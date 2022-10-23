"""delete_category_insert_subcategory

Revision ID: 87c7d29e3ddb
Revises: 35477a4b423e
Create Date: 2022-10-22 13:27:10.144666

"""
from sqlalchemy import select, insert, and_
from sqlalchemy.exc import ProgrammingError, InternalError
from app.database import db_session
from app.models import Users_Categories, Category


# revision identifiers, used by Alembic.
revision = '87c7d29e3ddb'
down_revision = '35477a4b423e'
branch_labels = None
depends_on = None


def get_user_categories():
    try:
        users_categories = db_session.scalars(
            select(Users_Categories).where(
                Users_Categories.category_id != None # noqa
            )
        ).all()
        delete_categories_insert_subcategories(users_categories)
    except ProgrammingError:
        pass
    except InternalError:
        pass


def delete_categories_insert_subcategories(users_categories):
    for user_category in users_categories:
        main_category_id = db_session.scalars(
            select(Category.id).where(
                Category.id == user_category.category_id, and_(
                    Category.parent_id == None # noqa
                )
            )
        ).first()
        if not main_category_id:
            continue
        subcategories_id = db_session.scalars(
            select(Category.id).where(
                Category.parent_id == main_category_id
            )
        ).all()
        main_category = db_session.scalars(
                select(Users_Categories).where(
                    Users_Categories.category_id == main_category_id
                )
        ).first()
        db_session.delete(main_category)
        for subcategory_id in subcategories_id:
            subcategory_exists = db_session.scalars(
                select(Users_Categories).where(
                    Users_Categories.category_id == subcategory_id
                )
            ).first()
            if not subcategory_exists:
                db_session.execute(
                    insert(Users_Categories).values(
                        telegram_id=user_category.telegram_id,
                        category_id=subcategory_id
                    )
                )
    db_session.commit()

def upgrade():
    get_user_categories()


def downgrade():
    pass
