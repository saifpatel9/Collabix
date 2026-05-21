from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return Response(
            {"success": False, "message": "An unexpected error occurred.", "data": {}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    detail = response.data
    message = detail.get("detail") if isinstance(detail, dict) else "Request failed."
    response.data = {
        "success": False,
        "message": message,
        "data": detail,
    }
    return response
