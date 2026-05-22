from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.core.models import Activity, AuditLog
from apps.core.services.search_service import GlobalSearchService


class GlobalSearchView(LoginRequiredMixin, TemplateView):
    template_name = "components/search_dropdown.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        context["query"] = query
        context["results"] = GlobalSearchService.search(query)
        return context


class RecentActivityPartialView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/partials/recent_activity_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["activities"] = Activity.objects.select_related("actor").order_by(
            "-timestamp"
        )[:10]
        return context


class AuditTimelineView(LoginRequiredMixin, TemplateView):
    template_name = "components/audit_timeline.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["audit_logs"] = AuditLog.objects.select_related("user").order_by(
            "-timestamp"
        )[:25]
        return context
