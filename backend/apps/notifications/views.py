from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView

from .models import Notification
from .services.notification_service import NotificationService


class NotificationDropdownView(LoginRequiredMixin, TemplateView):
    template_name = "components/notification_dropdown.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["notifications"] = NotificationService.recent_for(self.request.user)
        context["unread_count"] = NotificationService.unread_count(self.request.user)
        return context


class NotificationMarkReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        notification = get_object_or_404(
            Notification, pk=kwargs["pk"], recipient=request.user
        )
        NotificationService.mark_as_read(notification=notification, user=request.user)
        return redirect("notifications:dropdown")


class NotificationMarkAllReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        NotificationService.mark_all_read(user=request.user)
        return redirect("notifications:dropdown")
