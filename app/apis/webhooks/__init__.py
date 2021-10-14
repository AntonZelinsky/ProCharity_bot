from flask import Blueprint
from flask_restful import Api

from . import tasks
from . import categories
from . import analytics
from . import health_check

webhooks_bp = Blueprint('webhooks_bp', __name__)
wh_api = Api(webhooks_bp)

wh_api.add_resource(tasks.CreateTasks, '/api/v1/tasks/')
wh_api.add_resource(categories.CreateCategories, '/api/v1/categories/')
wh_api.add_resource(analytics.Analytics, '/api/v1/analytics/')
wh_api.add_resource(health_check.HealthCheck, '/api/v1/health_check/')
