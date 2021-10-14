from app import create_app
from bot import charity_bot

app = create_app()

if __name__ == "__main__":

    charity_bot.init()
    app.run()
