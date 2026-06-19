import gzip
import logging
import os
import shutil
import subprocess

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class BackupService:
    @staticmethod
    def backup_database():
        backup_dir = settings.DATABASE_BACKUP_DIR
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = timezone.now().strftime(
    "%Y%m%d_%H%M%S_%f"
)

        sql_file = (
            backup_dir /
            f"{settings.DATABASES['default']['NAME']}_{timestamp}.sql"
        )

        gzip_file = sql_file.with_suffix(".sql.gz")

        env = os.environ.copy()
        env["MYSQL_PWD"] = settings.DATABASES["default"]["PASSWORD"]

        command = [
            "mysqldump",
            f"--host={settings.DATABASES['default']['HOST']}",
            f"--port={settings.DATABASES['default']['PORT']}",
            f"--user={settings.DATABASES['default']['USER']}",
            settings.DATABASES["default"]["NAME"],
        ]

        with open(sql_file, "w") as dump:
            subprocess.run(
                command,
                stdout=dump,
                stderr=subprocess.PIPE,
                check=True,
                env=env,
            )

        with open(sql_file, "rb") as source:
            with gzip.open(gzip_file, "wb") as destination:
                shutil.copyfileobj(source, destination)

        sql_file.unlink()

        logger.info(
            "Database backup created: %s",
            gzip_file.name,
        )

        BackupService.cleanup_old_backups()

        return str(gzip_file)

    @staticmethod
    def cleanup_old_backups():
        backups = sorted(
            settings.DATABASE_BACKUP_DIR.glob("*.sql.gz"),
            key=lambda file: file.stat().st_mtime,
            reverse=True,
        )

        for old_file in backups[
            settings.DATABASE_BACKUP_RETENTION_COUNT:
        ]:
            old_file.unlink()

            logger.info(
                "Deleted old backup: %s",
                old_file.name,
            )