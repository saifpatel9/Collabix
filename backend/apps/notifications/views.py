from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, ListView, TemplateView

from .forms import NotificationPreferenceForm
from .models import Notification
from .services.notification_service import NotificationService


def is_htmx(request):
    return request.headers.get("HX-Request") == "true"


def dropdown_context(user, *, force_open=False):
    return {
        "notifications": NotificationService.recent_for(user),
        "unread_count": NotificationService.unread_count(user),
        "force_open": force_open,
    }


def notification_list_context(user, params, *, paginate_by=20):
    queryset = NotificationService.search_and_filter(
        NotificationService.for_user(user),
        status=params.get("status"),
        category=params.get("category"),
        search=params.get("q"),
    )
    paginator = Paginator(queryset, paginate_by)
    page_obj = paginator.get_page(params.get("page"))
    query = params.copy()
    query.pop("page", None)
    pagination_base_query = query.urlencode()
    if pagination_base_query:
        pagination_base_query += "&"
    return {
        "notifications": page_obj.object_list,
        "paginator": paginator,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages(),
        "categories": Notification.Category.choices,
        "filters": {
            "q": params.get("q", ""),
            "status": params.get("status", ""),
            "category": params.get("category", ""),
        },
        "pagination_base_query": pagination_base_query,
        "target": "#notification-list",
        "notification_widget_oob": dropdown_context(user),
    }


class NotificationDropdownView(LoginRequiredMixin, TemplateView):
    template_name = "components/notification_dropdown.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(dropdown_context(self.request.user))
        return context


class NotificationMarkReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        notification = get_object_or_404(
            Notification, pk=kwargs["pk"], recipient=request.user
        )
        NotificationService.mark_as_read(notification=notification, user=request.user)
        if is_htmx(request):
            if request.POST.get("response_scope") == "center":
                return render(
                    request,
                    "notifications/partials/notification_list.html",
                    notification_list_context(request.user, request.POST),
                )
            return render(
                request,
                "components/notification_dropdown.html",
                dropdown_context(request.user, force_open=True),
            )
        next_url = notification.action_url or "notifications:center"
        return redirect(next_url)


class NotificationMarkUnreadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        notification = get_object_or_404(
            Notification, pk=kwargs["pk"], recipient=request.user
        )
        NotificationService.mark_as_unread(notification=notification, user=request.user)
        if is_htmx(request):
            if request.POST.get("response_scope") == "center":
                return render(
                    request,
                    "notifications/partials/notification_list.html",
                    notification_list_context(request.user, request.POST),
                )
            return render(
                request,
                "components/notification_dropdown.html",
                dropdown_context(request.user, force_open=True),
            )
        next_url = notification.action_url or "notifications:center"
        return redirect(next_url)


class NotificationMarkAllReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        NotificationService.mark_all_read(user=request.user)
        if is_htmx(request):
            if request.POST.get("response_scope") == "center":
                return render(
                    request,
                    "notifications/partials/notification_list.html",
                    notification_list_context(request.user, request.POST),
                )
            return render(
                request,
                "components/notification_dropdown.html",
                dropdown_context(request.user, force_open=True),
            )
        return redirect("notifications:center")


class NotificationCenterView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "notifications/center.html"
    context_object_name = "notifications"
    paginate_by = 20

    def get_queryset(self):
        return NotificationService.search_and_filter(
            NotificationService.for_user(self.request.user),
            status=self.request.GET.get("status"),
            category=self.request.GET.get("category"),
            search=self.request.GET.get("q"),
        )

    def get_template_names(self):
        if self.request.headers.get("HX-Request") == "true":
            return ["notifications/partials/notification_list.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Notification.Category.choices
        context["filters"] = {
            "q": self.request.GET.get("q", ""),
            "status": self.request.GET.get("status", ""),
            "category": self.request.GET.get("category", ""),
        }
        query = self.request.GET.copy()
        query.pop("page", None)
        context["pagination_base_query"] = query.urlencode()
        if context["pagination_base_query"]:
            context["pagination_base_query"] += "&"
        context["target"] = "#notification-list"
        context["notification_widget_oob"] = dropdown_context(self.request.user)
        return context


class NotificationPreferenceView(LoginRequiredMixin, FormView):
    template_name = "notifications/preferences.html"
    form_class = NotificationPreferenceForm
    success_url = reverse_lazy("notifications:preferences")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = NotificationService.preferences_for(self.request.user)
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
