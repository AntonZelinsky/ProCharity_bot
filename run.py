from app import app
from app.database import init_db

if __name__ == "__main__":
    # init_db()  # initialize of database
    app.run()
