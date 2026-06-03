from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import TemplateView

from .forms import NotificationPreferenceForm
from .models import Notification, NotificationPreference
from .services.notification_service import NotificationService


class NotificationCenterView(LoginRequiredMixin, TemplateView):
    template_name = "notifications/center.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["notifications"] = Notification.objects.filter(
            recipient=self.request.user
        ).order_by("-created_at")[:50]
        context["unread_count"] = NotificationService.unread_count(self.request.user)
        return context


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

        if request.headers.get("HX-Request") == "true":
            html = render_to_string(
                "components/notification_dropdown.html",
                {
                    "notifications": NotificationService.recent_for(request.user),
                    "unread_count": NotificationService.unread_count(request.user),
                },
                request=request,
            )
            response = HttpResponse(html)
            response["HX-Trigger"] = "notification-read"
            return response

        return redirect(request.META.get("HTTP_REFERER", "dashboard:home"))


class NotificationPreferenceView(LoginRequiredMixin, TemplateView):
    template_name = "notifications/preferences.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        preference, _ = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        context["form"] = NotificationPreferenceForm(instance=preference)
        return context

    def post(self, request, *args, **kwargs):
        preference, _ = NotificationPreference.objects.get_or_create(
            user=request.user
        )
        form = NotificationPreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            return redirect("notifications:preferences")
        return self.render_to_response({"form": form})


class NotificationMarkAllReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        NotificationService.mark_all_read(user=request.user)

        if request.headers.get("HX-Request") == "true":
            html = render_to_string(
                "components/notification_dropdown.html",
                {
                    "notifications": NotificationService.recent_for(request.user),
                    "unread_count": NotificationService.unread_count(request.user),
                },
                request=request,
            )
            response = HttpResponse(html)
            response["HX-Trigger"] = "notification-read"
            return response

        return redirect(request.META.get("HTTP_REFERER", "dashboard:home"))


class NotificationPreferenceView(LoginRequiredMixin, TemplateView):
    template_name = "notifications/preferences.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        preference, _ = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        context["form"] = NotificationPreferenceForm(instance=preference)
        return context

    def post(self, request, *args, **kwargs):
        preference, _ = NotificationPreference.objects.get_or_create(
            user=request.user
        )
        form = NotificationPreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            return redirect("notifications:preferences")
        return self.render_to_response({"form": form})
