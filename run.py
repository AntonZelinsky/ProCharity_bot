from app import app
from app.database import init_db
from multiprocessing import Process
from bot.charity_bot import main

if __name__ == "__main__":
    # init_db()  # initialize of database
    app.run()

    _bot = Process(target=main)
    _bot.start()
