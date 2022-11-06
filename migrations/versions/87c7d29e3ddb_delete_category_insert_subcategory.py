"""delete_category_insert_subcategory

Revision ID: 87c7d29e3ddb
Revises: 35477a4b423e
Create Date: 2022-10-22 13:27:10.144666

"""
from sqlalchemy import select
from app.database import db_session
from app.models import Users_Categories, Category


# revision identifiers, used by Alembic.
revision = '87c7d29e3ddb'
down_revision = '35477a4b423e'
branch_labels = None
depends_on = None


def delete_main_category():
    users_categories = db_session.scalars(
        select(Users_Categories).join(Category).where(
            Category.parent_id == None
        )
    ).all()
    for user_categories in users_categories:
        db_session.delete(user_categories)
    db_session.commit()


def subscribe_to_subcategory():
    categories = set(db_session.scalars(
        select(Category).join(Users_Categories)
    ).all())
    for category in categories:
        if category.children:
            for user in category.users:
                subcategories = [Users_Categories(telegram_id=user.telegram_id, category_id=children.id) for children in category.children if children not in user.categories]
                db_session.add_all(subcategories)


def upgrade():
    subscribe_to_subcategory()
    delete_main_category()


def downgrade():
    pass
