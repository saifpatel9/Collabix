from .base import *  # noqa: F403,F401

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INSTALLED_APPS += ["django_extensions"]  # noqa: F405

CELERY_TASK_ALWAYS_EAGER = True

import os
if os.getenv("DJANGO_FORCE_SQLITE", "False").lower() == "true" or not os.getenv("MYSQL_HOST"):
    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parents[2]
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(BASE_DIR / "db.sqlite3"),
        }
    }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
        "verbose": {
            "format": "%(asctime)s [%(levelname)s] %(name)s %(module)s:%(lineno)d: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
}
