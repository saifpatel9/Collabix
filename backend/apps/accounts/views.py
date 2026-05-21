from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import DetailView, UpdateView

from .forms import ProfileUpdateForm
from .models import User
from .services.profile_service import ProfileService


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
