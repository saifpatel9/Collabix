import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    view = context.get("view")
    view_name = view.__class__.__name__ if view else "UnknownView"

    if response is None:
        logger.exception(
            "Unhandled API exception in %s",
            view_name,
        )

        return Response(
            {
                "success": False,
                "message": "An unexpected error occurred.",
                "data": {},
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    logger.warning(
        "API exception in %s status=%s exception=%s",
        view_name,
        response.status_code,
        exc.__class__.__name__,
    )

    detail = response.data

    message = (
        detail.get("detail")
        if isinstance(detail, dict)
        else "Request failed."
    )

    response.data = {
        "success": False,
        "message": message,
        "data": detail,
    }

    return response