from flask import Blueprint
from flask_restful import Api


notifications_bp = Blueprint('notifications_bp', __name__)
nf_api = Api(notifications_bp)

from . import send_tg_notification

nf_api.add_resource(send_tg_notification.SendTelegramNotification,
                    '/api/v1/send_telegram_notification/')