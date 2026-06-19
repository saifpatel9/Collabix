import logging
import subprocess

from celery import shared_task
from django.core.management import call_command

from apps.core.services.backup_service import BackupService

from apps.core.services.media_backup_service import (
    MediaBackupService,
)
from apps.core.services.restore_verification_service import (
    RestoreVerificationService,
)
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


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def backup_media():
    logger.info(
        "Starting media backup"
    )

    backup_path = (
        MediaBackupService.backup_media()
    )

    logger.info(
        "Media backup completed: %s",
        backup_path,
    )

    return backup_path

@shared_task(
    autoretry_for=(subprocess.CalledProcessError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def verify_database_backup():
    logger.info(
        "Starting database restore verification"
    )

    result = (
        RestoreVerificationService
        .verify_latest_database_backup()
    )

    logger.info(
        "Database restore verification completed"
    )

    return result