import logging

from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


logger = logging.getLogger(__name__)


class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        # Cache URL paths once
        self.password_change_path = reverse("accounts:change_password")
        self.logout_path = reverse("accounts:logout")
        self.password_reset_done_path = reverse("accounts:password_reset_done")

        self.safe_paths = {
            self.password_change_path.rstrip("/"),
            self.logout_path.rstrip("/"),
            self.password_reset_done_path.rstrip("/"),
        }

    def __call__(self, request):
        path = request.path

        # Skip admin
        if path.startswith(reverse("admin:index")):
            return self.get_response(request)

        # Skip static/media
        if settings.STATIC_URL and path.startswith(settings.STATIC_URL):
            return self.get_response(request)

        if settings.MEDIA_URL and path.startswith(settings.MEDIA_URL):
            return self.get_response(request)

        # Skip APIs
        if path.startswith("/api/"):
            return self.get_response(request)

        user = getattr(request, "user", None)

        # Anonymous users proceed normally
        if not user or not user.is_authenticated:
            return self.get_response(request)

        # User already changed password
        if not getattr(user, "must_change_password", False):
            return self.get_response(request)

        current_path = path.rstrip("/")

        # Allow access to password-related pages
        if current_path in self.safe_paths:
            return self.get_response(request)

        logger.info(
            "Redirecting user %s to password change page",
            getattr(user, "email", user.pk),
        )

        return redirect("accounts:change_password")