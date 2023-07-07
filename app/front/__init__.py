from flask import Blueprint
from flask_restful import Api


front_bp = Blueprint('front_bp', __name__)
front_api = Api(front_bp)

from . import analytics
from . import send_tg_notification
from . import send_tg_message_to_user
from . import users
from . import download_log_files

front_api.add_resource(analytics.Analytics, '/api/v1/analytics/')
front_api.add_resource(send_tg_notification.SendTelegramNotification,
                       '/api/v1/messages/')
front_api.add_resource(send_tg_message_to_user.SendTelegramMessage,
                       '/api/v1/messages/<int:telegram_id>/')
front_api.add_resource(users.UsersList, '/api/v1/users/')
front_api.add_resource(users.UserItem, '/api/v1/users/<int:telegram_id>/')
front_api.add_resource(download_log_files.DownloadLogs, '/api/v1/download_logs/')
front_api.add_resource(download_log_files.GetListLogFiles, '/api/v1/logs/')
