import os
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.basename(os.getenv('DATABASE_URL'))
DB_PATH = os.path.join(BASE_DIR, DB_NAME)

engine = create_engine('sqlite:///' + DB_PATH)


def get_category():
    with engine.connect() as conn:
        metadata = MetaData(engine)
        category = Table('category', metadata, autoload=True)
        stmt = select(category.c.name)
        res = conn.execute(stmt)
        return [i[0] for i in res]


def get_task():
    with engine.connect() as conn:
        metadata = MetaData(engine)
        tasks = Table('task', metadata, autoload=True)
        stmt = select(tasks)
        res = conn.execute(stmt)
        return [i for i in res]


def display_task(t):
    tasks = [f'Организация: {organization}\nЗадание: {title}\nДедлайн: {deadline}\nСсылка на задание: {link}'
             for iden, task_api_id, title, organization, deadline, category_id, bonus, location, link, desc, user_id
             in t]

    return '\n\n'.join(tasks)
