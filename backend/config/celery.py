import os
import logging

from celery import Celery

logger = logging.getLogger(__name__)

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    os.getenv("DJANGO_SETTINGS_MODULE", "config.settings.development"),
)

app = Celery("collabix")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    logger.info("Celery debug task executed: {self.request!r}")
