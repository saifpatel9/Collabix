from .base import *  # noqa: F403,F401

DEBUG = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INSTALLED_APPS += ["django_extensions"]  # noqa: F405

# Development convenience: if MySQL isn't configured locally, fall back to a
# lightweight SQLite database so `runserver` and migrations work out-of-the-box.
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
