from app import docs
from app.front.analytics import Analytics
from app.front.download_log_files import DownloadLogs, GetListLogFiles
from app.front.users import UsersList, UserItem
from app.front.send_tg_notification import SendTelegramNotification
from app.front.send_tg_message_to_user import SendTelegramMessage


docs.register(Analytics, blueprint='front_bp')
docs.register(SendTelegramNotification, blueprint='front_bp')
docs.register(SendTelegramMessage, blueprint='front_bp')
docs.register(UsersList, blueprint='front_bp')
docs.register(UserItem, blueprint='front_bp')
docs.register(DownloadLogs, blueprint='front_bp')
docs.register(GetListLogFiles, blueprint='front_bp')
