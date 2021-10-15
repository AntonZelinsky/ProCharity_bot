from app import docs
from app.webhooks.categories import CreateCategories
from app.webhooks.health_check import HealthCheck
from app.webhooks.tasks import CreateTasks


docs.register(CreateCategories, blueprint='webhooks_bp')
docs.register(CreateTasks, blueprint='webhooks_bp')
docs.register(HealthCheck, blueprint='webhooks_bp')
