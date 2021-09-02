from app import create_app
from bot import charity_bot

if __name__ == "__main__":
    app = create_app()

    charity_bot.init()
    app.run()
