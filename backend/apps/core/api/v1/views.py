from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.core.api.responses import api_response


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return api_response(message="Collabix API is healthy.", data={"status": "ok"})
