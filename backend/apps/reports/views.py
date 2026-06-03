import json

from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView, View

from apps.core.mixins import PageSizeMixin
from apps.core.permissions import (
    AdminRequiredMixin,
    EmployeeAccessMixin,
    ManagerRequiredMixin,
    RoleRequiredMixin,
)
from apps.reports.forms import ReportConfigForm, ReportFilterForm
from apps.reports.models import ReportConfig, ReportExport
from apps.reports.selectors.analytics_selector import AnalyticsSelector
from apps.reports.selectors.report_selector import ReportSelector
from apps.reports.services.analytics_service import AnalyticsService
from apps.reports.services.export_service import ExportService
from apps.reports.services.report_service import ReportService


class AnalyticsDashboardView(EmployeeAccessMixin, TemplateView):
    """Main analytics dashboard with KPI cards and charts."""
    template_name = "reports/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        svc = AnalyticsService()
        ctx["kpis"] = svc.kpi_dashboard(self.request.user)
        ctx["tasks_by_status"] = AnalyticsSelector.task_stats()
        ctx["project_stats"] = AnalyticsSelector.project_stats()
        ctx["recent_exports"] = ReportSelector.recent_exports(self.request.user)
        ctx["filter_form"] = ReportFilterForm()
        return ctx


class PerformanceAnalyticsView(EmployeeAccessMixin, TemplateView):
    template_name = "reports/performance.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        svc = AnalyticsService()
        filters = {}
        if self.request.GET.get("department"):
            filters["department_id"] = self.request.GET.get("department")
        data = svc.employee_performance(filters if filters else None)
        ctx["performance_data"] = data
        ctx["filter_form"] = ReportFilterForm(self.request.GET)
        ctx["summary"] = {
            "avg_completion_rate": round(sum(e["completion_rate"] for e in data) / len(data), 1) if data else 0,
            "total_tasks": sum(e["total_tasks"] for e in data),
            "total_overdue": sum(e["overdue_tasks"] for e in data),
        }
        return ctx


class ProductivityAnalyticsView(EmployeeAccessMixin, TemplateView):
    template_name = "reports/productivity.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        svc = AnalyticsService()
        data = svc.team_productivity(
            department_id=self.request.GET.get("department"),
        )
        ctx["productivity_data"] = data
        ctx["filter_form"] = ReportFilterForm(self.request.GET)
        ctx["summary"] = {
            "total_employees": sum(d["employee_count"] for d in data),
            "total_tasks": sum(d["total_tasks"] for d in data),
            "completed_tasks": sum(d["completed_tasks"] for d in data),
        }
        return ctx


class ProjectAnalyticsView(EmployeeAccessMixin, TemplateView):
    template_name = "reports/projects.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        svc = AnalyticsService()
        ctx["project_data"] = svc.project_progress(
            project_id=self.request.GET.get("project"),
        )
        ctx["milestone_stats"] = AnalyticsSelector.milestone_stats(
            project_id=self.request.GET.get("project"),
        )
        ctx["filter_form"] = ReportFilterForm(self.request.GET)
        return ctx


class TaskAnalyticsView(EmployeeAccessMixin, TemplateView):
    template_name = "reports/tasks.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        filters = {}
        if self.request.GET.get("project"):
            filters["project_id"] = self.request.GET.get("project")
        if self.request.GET.get("status"):
            filters["status"] = self.request.GET.get("status")
        svc = AnalyticsService()
        ctx["task_stats"] = svc.task_analytics(filters=filters if filters else None)
        ctx["workflow"] = svc.workflow_efficiency()
        ctx["completion_trends"] = AnalyticsSelector.completion_trends(days=30)
        ctx["overdue_tasks"] = AnalyticsSelector.overdue_tasks(filters=filters if filters else None)
        ctx["bottlenecks"] = AnalyticsSelector.bottleneck_tasks()
        ctx["filter_form"] = ReportFilterForm(self.request.GET)
        return ctx


class AttendanceAnalyticsView(EmployeeAccessMixin, TemplateView):
    template_name = "reports/attendance.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        svc = AnalyticsService()
        ctx["attendance_data"] = svc.attendance_analytics(
            department_id=self.request.GET.get("department"),
        )
        ctx["monthly_trend"] = AnalyticsSelector.monthly_attendance_trend(months=6)
        ctx["filter_form"] = ReportFilterForm(self.request.GET)
        return ctx


class WorkflowAnalyticsView(EmployeeAccessMixin, TemplateView):
    template_name = "reports/workflow.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        svc = AnalyticsService()
        ctx["workflow"] = svc.workflow_efficiency()
        ctx["bottleneck"] = svc.bottleneck_analysis()
        ctx["workload"] = svc.workload_distribution()
        ctx["sla_breaches"] = svc.sla_breaches(days=30)
        return ctx


# ── Report CRUD ────────────────────────────────────────────

class ReportListView(EmployeeAccessMixin, PageSizeMixin, ListView):
    model = ReportConfig
    template_name = "reports/report_list.html"
    context_object_name = "reports"
    paginate_by = 20

    def get_queryset(self):
        qs = ReportSelector.reports_for_user(self.request.user)
        report_type = self.request.GET.get("type")
        if report_type:
            qs = qs.filter(report_type=report_type)
        search = self.request.GET.get("q")
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["report_types"] = ReportConfig.REPORT_TYPES
        ctx["current_type"] = self.request.GET.get("type", "")
        ctx["search_query"] = self.request.GET.get("q", "")
        return ctx


class ReportCreateView(EmployeeAccessMixin, CreateView):
    model = ReportConfig
    form_class = ReportConfigForm
    template_name = "reports/report_form.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Report configuration created successfully.")
        return response

    def get_success_url(self):
        return reverse("reports:report_detail", kwargs={"pk": self.object.pk})


class ReportDetailView(EmployeeAccessMixin, DetailView):
    model = ReportConfig
    template_name = "reports/report_detail.html"
    context_object_name = "report"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["exports"] = ReportSelector.exports_for_report(self.object.pk)
        return ctx


class ReportUpdateView(EmployeeAccessMixin, UpdateView):
    model = ReportConfig
    form_class = ReportConfigForm
    template_name = "reports/report_form.html"

    def get_success_url(self):
        return reverse("reports:report_detail", kwargs={"pk": self.object.pk})


class ReportDeleteView(EmployeeAccessMixin, DeleteView):
    model = ReportConfig
    template_name = "reports/report_confirm_delete.html"
    context_object_name = "report"

    def get_success_url(self):
        messages.success(self.request, "Report deleted successfully.")
        return reverse("reports:report_list")


class ReportGenerateView(EmployeeAccessMixin, View):
    def post(self, request, pk):
        report = get_object_or_404(ReportConfig, pk=pk, created_by=request.user)
        export = ReportService.generate_report(report)
        if export.status == "completed":
            messages.success(request, "Report generated successfully.")
        else:
            messages.error(request, f"Report generation failed: {export.error_message}")
        return redirect("reports:report_detail", pk=pk)


class ReportDownloadView(EmployeeAccessMixin, View):
    def get(self, request, pk, export_id):
        export = get_object_or_404(ReportExport, pk=export_id, report__created_by=request.user)
        if export.status != "completed" or not export.file:
            messages.error(request, "Export file not available.")
            return redirect("reports:report_detail", pk=pk)
        response = JsonResponse({"url": export.file.url})
        return redirect(export.file.url)


class ReportExportView(EmployeeAccessMixin, View):
    def get(self, request, pk, export_format):
        report = get_object_or_404(ReportConfig, pk=pk, created_by=request.user)
        export = ReportService.generate_report(report)
        if export.status == "completed" and export.file:
            return redirect(export.file.url)
        messages.error(request, "Export failed. Please try again.")
        return redirect("reports:report_detail", pk=pk)


class ReportScheduleView(EmployeeAccessMixin, UpdateView):
    model = ReportConfig
    fields = ["is_scheduled", "frequency", "export_format", "recipients"]
    template_name = "reports/report_schedule.html"
    context_object_name = "report"

    def get_success_url(self):
        messages.success(self.request, "Report schedule updated.")
        return reverse("reports:report_detail", kwargs={"pk": self.object.pk})


# ── API / HTMX Endpoints ──────────────────────────────────

class KpiDataView(EmployeeAccessMixin, View):
    """Returns JSON KPI data for chart updates."""
    def get(self, request):
        svc = AnalyticsService()
        kpis = svc.kpi_dashboard(request.user)
        return JsonResponse(kpis)


class ChartDataView(EmployeeAccessMixin, View):
    """Returns JSON chart data."""
    def get(self, request):
        chart_type = request.GET.get("chart", "tasks_by_status")
        data = {}

        if chart_type == "tasks_by_status":
            stats = AnalyticsSelector.task_stats()
            data = {
                "labels": ["To Do", "In Progress", "Done", "Review", "Blocked"],
                "values": [stats["todo"], stats["in_progress"], stats["done"], stats["review"], stats["blocked"]],
                "colors": ["#f59e0b", "#3b82f6", "#10b981", "#8b5cf6", "#ef4444"],
            }
        elif chart_type == "projects_by_status":
            ps = AnalyticsSelector.projects_by_status()
            data = {
                "labels": list(ps.keys()),
                "values": list(ps.values()),
            }
        elif chart_type == "completion_trends":
            trends = AnalyticsSelector.completion_trends(days=30)
            data = {
                "labels": [t["date"] for t in trends],
                "values": [t["count"] for t in trends],
            }
        elif chart_type == "monthly_attendance":
            trends = AnalyticsSelector.monthly_attendance_trend(months=6)
            data = {
                "labels": [t["month"] for t in trends],
                "present": [t["present"] for t in trends],
                "absent": [t["absent"] for t in trends],
            }
        elif chart_type == "workload":
            workload = AnalyticsSelector.workload_distribution()[:10]
            data = {
                "labels": [w["name"] for w in workload],
                "values": [w["load_score"] for w in workload],
            }

        return JsonResponse(data)


class TasksByPriorityView(EmployeeAccessMixin, View):
    def get(self, request):
        data = AnalyticsSelector.tasks_by_priority()
        return JsonResponse(dict(data))


class WorkloadDataView(EmployeeAccessMixin, View):
    def get(self, request):
        dept_id = request.GET.get("department")
        data = AnalyticsSelector.workload_distribution(department_id=dept_id)
        return JsonResponse({"workload": data})
