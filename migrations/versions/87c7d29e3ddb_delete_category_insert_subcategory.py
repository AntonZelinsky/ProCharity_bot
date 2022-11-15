"""delete_category_insert_subcategory

Revision ID: 87c7d29e3ddb
Revises: 52647dd43d55
Create Date: 2022-10-22 13:27:10.144666

"""
from sqlalchemy import select
from app.database import db_session
from app.models import Users_Categories, Category


# revision identifiers, used by Alembic.
revision = '87c7d29e3ddb'
down_revision = '52647dd43d55'
branch_labels = None
depends_on = None


def upgrade():
    categories = set(
        db_session.execute(
            select(Category).join(Users_Categories).where(Category.children is not None)
        ).scalars()
    )

    for category in categories:
        for user in category.users:
            subcategories = [Users_Categories(telegram_id=user.telegram_id, category_id=children.id) for children in category.children if children not in user.categories]
            db_session.add_all(subcategories)
        category.users = []
    db_session.commit()


def downgrade():
    pass
