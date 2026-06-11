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


from celery.signals import worker_process_init

@worker_process_init.connect
def reset_process_state(**kwargs):
    from app.llm.client import reset_client
    from app.db import configure_null_pool, reset_engine
    configure_null_pool()
    reset_client()
    reset_engine()
