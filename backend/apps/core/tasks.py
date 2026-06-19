import logging

from celery import shared_task
from django.core.management import call_command

from apps.core.services.backup_service import BackupService

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
    

@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def backup_database():
    logger.info("Starting database backup")

    backup_path = BackupService.backup_database()

    logger.info(
        "Database backup completed: %s",
        backup_path,
    )

    return backup_path