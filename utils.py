import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.basename(os.getenv('DATABASE_URL'))
DB_PATH = os.path.join(BASE_DIR, DB_NAME)


def get_category():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('select * from category')

    return [i[2] for i in cursor]
