import gzip
import logging
import os
import subprocess
import tempfile

from django.conf import settings

logger = logging.getLogger(__name__)


class RestoreVerificationService:
    @staticmethod
    def verify_latest_database_backup():
        backups = sorted(
            settings.DATABASE_BACKUP_DIR.glob("*.sql.gz"),
            key=lambda file: file.stat().st_mtime,
            reverse=True,
        )

        if not backups:
            raise FileNotFoundError(
                "No database backups found."
            )

        latest_backup = backups[0]
        test_database = settings.RESTORE_TEST_DATABASE

        logger.info(
            "Verifying backup: %s",
            latest_backup.name,
        )

        env = os.environ.copy()
        env["MYSQL_PWD"] = settings.MYSQL_ROOT_PASSWORD

        with tempfile.NamedTemporaryFile(
            suffix=".sql",
            delete=False,
        ) as temp_sql:
            temp_sql_path = temp_sql.name

        try:
            with gzip.open(latest_backup, "rb") as source:
                with open(temp_sql_path, "wb") as destination:
                    destination.write(source.read())

            subprocess.run(
                [
                    "mysql",
                    f"--host={settings.DATABASES['default']['HOST']}",
                    f"--port={settings.DATABASES['default']['PORT']}",
                    "--user=root",
                    "-e",
                    (
                        f"DROP DATABASE IF EXISTS {test_database};"
                        f"CREATE DATABASE {test_database};"
                    ),
                ],
                check=True,
                env=env,
            )

            with open(temp_sql_path, "rb") as sql_file:
                subprocess.run(
                    [
                        "mysql",
                        f"--host={settings.DATABASES['default']['HOST']}",
                        f"--port={settings.DATABASES['default']['PORT']}",
                        "--user=root",
                        test_database,
                    ],
                    stdin=sql_file,
                    check=True,
                    env=env,
                )

            critical_tables = [
                "django_migrations",
                "users",
                "employee_profiles",
            ]

            for table in critical_tables:
                subprocess.run(
                    [
                        "mysql",
                        f"--host={settings.DATABASES['default']['HOST']}",
                        f"--port={settings.DATABASES['default']['PORT']}",
                        "--user=root",
                        test_database,
                        "-e",
                        f"SELECT COUNT(*) FROM `{table}`;",
                    ],
                    check=True,
                    env=env,
                )

            logger.info(
                "Backup verification successful: %s",
                latest_backup.name,
            )

            return {
                "success": True,
                "backup": latest_backup.name,
            }

        finally:
            subprocess.run(
                [
                    "mysql",
                    f"--host={settings.DATABASES['default']['HOST']}",
                    f"--port={settings.DATABASES['default']['PORT']}",
                    "--user=root",
                    "-e",
                    f"DROP DATABASE IF EXISTS {test_database};",
                ],
                env=env,
            )

            if os.path.exists(temp_sql_path):
                os.remove(temp_sql_path)