from rest_framework.response import Response


def api_response(*, success: bool = True, message: str = "", data=None, status_code: int = 200):
    payload = {
        "success": success,
        "message": message,
        "data": data if data is not None else {},
    }
    return Response(payload, status=status_code)
