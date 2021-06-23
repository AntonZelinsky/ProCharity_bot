from app import app
from multiprocessing import Process
from bot.charity_bot import main

if __name__ == "__main__":
    app.run()

    _bot = Process(target=main)
    _bot.run()
