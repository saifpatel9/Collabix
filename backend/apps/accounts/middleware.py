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
            print("SKIPPED: admin")
            return self.get_response(request)

        if request.path.startswith(settings.STATIC_URL):
            print("SKIPPED: static")
            return self.get_response(request)

        if request.path.startswith(settings.MEDIA_URL):
            print("SKIPPED: media")
            return self.get_response(request)

        if request.path.startswith("/api/"):
            print("SKIPPED: api")
            return self.get_response(request)

        # Get user if available
        user = getattr(request, "user", None)


        if not user or not user.is_authenticated:
            print("RETURNING: anonymous user")
            return self.get_response(request)

        # If user doesn't need to change password, proceed
        if not getattr(user, "must_change_password", False):
            print("RETURNING: password change NOT required")
            return self.get_response(request)

        # Define safe paths where redirect shouldn't happen
        try:
            password_change_path = reverse("accounts:change_password")
            logout_path = reverse("accounts:logout")
            password_reset_done_path = reverse("accounts:password_reset_done")
        except Exception as e:
            print("REVERSE ERROR:", e)
            return self.get_response(request)

        safe_paths = [
            password_change_path,
            logout_path,
            password_reset_done_path,
        ]

        # Normalize paths by removing trailing slashes
        def normalize(path):
            return path.rstrip("/")

        current_path_normalized = normalize(request.path)
        safe_paths_normalized = [normalize(p) for p in safe_paths]

        # If current path is safe, proceed
        if current_path_normalized in safe_paths_normalized:
            print("RETURNING: safe path")
            return self.get_response(request)

        # Otherwise, redirect to password change page
        return redirect("accounts:change_password")