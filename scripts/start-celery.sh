#!/bin/sh
set -e

exec celery -A config.celery worker \
    --loglevel="${CELERY_LOG_LEVEL:-info}" \
    --concurrency="${CELERY_WORKER_CONCURRENCY:-4}" \
    --max-tasks-per-child="${CELERY_MAX_TASKS_PER_CHILD:-1000}" \
    --time-limit="${CELERY_TASK_TIME_LIMIT:-1800}" \
    --soft-time-limit="${CELERY_TASK_SOFT_TIME_LIMIT:-1500}" \
    --prefetch-multiplier="${CELERY_PREFETCH_MULTIPLIER:-1}" \
    --events