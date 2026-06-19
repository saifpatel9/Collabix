import logging
import tarfile

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class MediaBackupService:
    @staticmethod
    def backup_media():
        backup_dir = settings.MEDIA_BACKUP_DIR
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = timezone.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        archive_file = (
            backup_dir /
            f"media_{timestamp}.tar.gz"
        )

        with tarfile.open(
            archive_file,
            "w:gz",
        ) as archive:
            archive.add(
                settings.MEDIA_ROOT,
                arcname="media",
            )

        logger.info(
            "Media backup created: %s",
            archive_file.name,
        )

        MediaBackupService.cleanup_old_backups()

        return str(archive_file)

    @staticmethod
    def cleanup_old_backups():
        backups = sorted(
            settings.MEDIA_BACKUP_DIR.glob(
                "*.tar.gz"
            ),
            key=lambda file: file.stat().st_mtime,
            reverse=True,
        )

        for old_file in backups[
            settings.MEDIA_BACKUP_RETENTION_COUNT:
        ]:
            old_file.unlink()

            logger.info(
                "Deleted old media backup: %s",
                old_file.name,
            )