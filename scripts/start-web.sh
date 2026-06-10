#!/bin/sh
set -e

exec gunicorn config.asgi:application \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-3}" \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --graceful-timeout "${GUNICORN_GRACEFUL_TIMEOUT:-30}" \
    --keep-alive "${GUNICORN_KEEP_ALIVE:-5}" \
    --max-requests "${GUNICORN_MAX_REQUESTS:-10000}" \
    --max-requests-jitter "${GUNICORN_MAX_REQUESTS_JITTER:-1000}" \
    --worker-tmp-dir /dev/shm \
    --access-logfile - \
    --access-logformat '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"' \
    --error-logfile - \
    --log-level "${GUNICORN_LOG_LEVEL:-info}"