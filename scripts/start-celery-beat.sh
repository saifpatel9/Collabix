#!/bin/sh
set -e

exec celery -A config.celery beat \
    --loglevel="${CELERY_LOG_LEVEL:-info}" \
    --schedule=/app/backend/logs/celerybeat-schedule