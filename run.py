from app.app_init import app
from bot import charity_bot


if __name__ == "__main__":
    charity_bot.init()
    app.run()
