import logging
import random

from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.utils import OperationalError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, UpdateView, CreateView
from django.views import View

from .forms import (
    EmailAuthenticationForm,
    ProfileUpdateForm,
    CustomPasswordChangeForm,
    CustomSetPasswordForm,
    ForgotPasswordForm,
)
from .models import LoginHistory, OTPCode, User
from .services.profile_service import ProfileService


logger = logging.getLogger(__name__)


def _record_login(request, user, method=LoginHistory.LoginMethod.PASSWORD, success=True, reason=""):
    try:
        LoginHistory.objects.create(
            user=user,
            ip_address=request.META.get("REMOTE_ADDR", ""),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
            method=method,
            success=success,
            failure_reason=reason,
            session_key=request.session.session_key or "",
        )
    except OperationalError as e:
        logger.warning("Failed to record login history (table may not exist yet): %s", e)


class LoginView(auth_views.LoginView):
    form_class = EmailAuthenticationForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def form_invalid(self, form):
        attempts = self.request.session.get("login_attempts", 0) + 1
        self.request.session["login_attempts"] = attempts
        self.request.session["login_attempt_time"] = timezone.now().isoformat()

        email = form.cleaned_data.get("username", "")
        if email:
            try:
                user = User.objects.get(email__iexact=email)
                _record_login(self.request, user, success=False, reason="invalid_password")
                if not user.is_active:
                    messages.error(self.request, "This account has been deactivated.")
                    return self.render_to_response(self.get_context_data(form=form))
            except User.DoesNotExist:
                User().set_password("dummy")

        if attempts >= 5:
            messages.error(
                self.request,
                "Too many login attempts. Please wait and try again.",
            )

        return super().form_invalid(form)

    def form_valid(self, form):
        self.request.session.pop("login_attempts", None)
        self.request.session.pop("login_attempt_time", None)

        user = form.get_user()
        _record_login(self.request, user)

        remember = form.cleaned_data.get("remember")
        response = super().form_valid(form)
        if not remember:
            self.request.session.set_expiry(0)
        return response

    def get_success_url(self):
        user = self.request.user
        if user.must_change_password:
            return reverse_lazy("accounts:change_password")
        if user.role in (User.Role.ADMIN, User.Role.DEPARTMENT_ADMIN):
            return reverse_lazy("dashboard:home")
        if user.role == User.Role.PROJECT_MANAGER:
            return reverse_lazy("projects:list")
        if user.role in (User.Role.MANAGER, User.Role.HR_MANAGER):
            return reverse_lazy("employees:list")
        return reverse_lazy("dashboard:home")


class CustomPasswordChangeView(auth_views.PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = "accounts/change_password.html"
    success_url = reverse_lazy("accounts:password_change_done")

    def form_valid(self, form):
        self.request.user.must_change_password = False
        self.request.user.save(update_fields=["must_change_password", "updated_at"])
        messages.success(self.request, "Your password has been changed successfully.")
        return super().form_valid(form)


class CustomPasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = "accounts/change_password_done.html"


class ProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "accounts/profile.html"
    context_object_name = "profile_user"

    def get_object(self, queryset=None):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
    template_name = "accounts/profile_form.html"

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        ProfileService.update_profile(
            user=self.request.user, cleaned_data=form.cleaned_data
        )
        messages.success(self.request, "Profile updated successfully.")
        return redirect("accounts:profile")


@login_required
def login_history_view(request):
    try:
        history = LoginHistory.objects.filter(user=request.user)
        paginator = Paginator(history, 25)
        page_number = request.GET.get("page", 1)
        page_obj = paginator.get_page(page_number)
    except OperationalError:
        page_obj = []
    return render(request, "accounts/login_history.html", {"page_obj": page_obj})
