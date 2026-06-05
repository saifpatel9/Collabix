from django.shortcuts import redirect
from django.urls import reverse


class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip middleware if user isn't authenticated
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return self.get_response(request)

        # Define paths that are allowed even if password change is required
        allowed_paths = [
            reverse('accounts:change_password'),
            reverse('accounts:logout'),
        ]

        # Check if current path is in allowed paths
        if request.path in allowed_paths:
            return self.get_response(request)

        # Check if user must change password
        if request.user.must_change_password:
            return redirect('accounts:change_password')

        return self.get_response(request)
