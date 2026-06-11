from celery import Celery
from app.config import get_settings

def make_celery() -> Celery:
    s = get_settings()
    app = Celery("pipeline_a", broker=s.REDIS_URL, backend=s.REDIS_URL)
    app.conf.task_serializer = "json"
    app.conf.result_serializer = "json"
    app.autodiscover_tasks(["app.pipeline.tasks"])
    return app

celery_app = make_celery()
