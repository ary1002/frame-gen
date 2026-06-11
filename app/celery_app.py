from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery("pipeline_a")

celery_app.conf.broker_url = settings.REDIS_URL
celery_app.conf.result_backend = settings.REDIS_URL
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.timezone = "UTC"
celery_app.conf.enable_utc = True

celery_app.autodiscover_tasks(["app.pipeline.tasks"])
