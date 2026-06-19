import logging

from celery import shared_task
from django.core.management import call_command

logger = logging.getLogger(__name__)


@shared_task
def health_check():
    logger.info("Starting health check task")

    logger.info("Health check task completed")

    return "ok"


@shared_task
def clear_expired_sessions():
    logger.info("Starting clear expired sessions task")

    call_command("clearsessions")

    logger.info("Clear expired sessions task completed")