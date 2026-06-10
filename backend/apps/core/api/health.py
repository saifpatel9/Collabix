import logging

import redis
from celery import current_app
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def health_check(request):
    status = {"status": "ok", "version": "1.0.0"}

    try:
        cache.set("health_check", "ok", 5)
        cache.get("health_check")
        status["cache"] = "ok"
    except Exception as e:
        status["cache"] = f"error: {e}"
        status["status"] = "degraded"

    try:
        conn = redis.Redis.from_url(settings.REDIS_URL)
        conn.ping()
        conn.close()
        status["redis"] = "ok"
    except Exception as e:
        status["redis"] = f"error: {e}"
        status["status"] = "degraded"

    try:
        celery_app = current_app
        celery_app.control.ping(timeout=3.0)
        status["celery"] = "ok"
    except Exception as e:
        status["celery"] = f"error: {e}"
        status["status"] = "degraded"

    try:
        from django.db import connections
        connections["default"].cursor()
        status["database"] = "ok"
    except Exception as e:
        status["database"] = f"error: {e}"
        status["status"] = "degraded"

    status_code = 200 if status["status"] == "ok" else 503
    return JsonResponse(status, status=status_code)
