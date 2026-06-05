from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings


class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip middleware entirely for:
        # - Admin URLs
        # - Static/media files
        # - API URLs (if any)
        if request.path.startswith(reverse("admin:index")):
            return self.get_response(request)
        if request.path.startswith(settings.STATIC_URL):
            return self.get_response(request)
        if request.path.startswith(settings.MEDIA_URL):
            return self.get_response(request)
        if request.path.startswith("/api/"):
            return self.get_response(request)

        # Get user if available
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return self.get_response(request)

        # If user doesn't need to change password, proceed
        if not getattr(user, "must_change_password", False):
            return self.get_response(request)

        # Define safe paths where redirect shouldn't happen
        try:
            password_change_path = reverse("accounts:change_password")
            logout_path = reverse("accounts:logout")
            password_reset_done_path = reverse("accounts:password_reset_done")
            verify_otp_path = reverse("accounts:verify_otp")
            forgot_password_path = reverse("accounts:forgot_password_otp")
        except Exception:
            return self.get_response(request)

        safe_paths = [
            password_change_path,
            logout_path,
            password_reset_done_path,
            verify_otp_path,
            forgot_password_path,
        ]

        # Normalize paths by removing trailing slashes
        def normalize(path):
            return path.rstrip("/")

        current_path_normalized = normalize(request.path)
        safe_paths_normalized = [normalize(p) for p in safe_paths]

        # If current path is safe, proceed
        if current_path_normalized in safe_paths_normalized:
            return self.get_response(request)

        # Otherwise, redirect to password change page
        return redirect("accounts:change_password")
