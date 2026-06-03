from django.db.models import Q

from apps.reports.models import ReportConfig, ReportDashboard, ReportExport


class ReportSelector:
    """Read-only queries for reports."""

    @staticmethod
    def reports_for_user(user, report_type=None):
        q = Q(created_by=user)
        if report_type:
            q &= Q(report_type=report_type)
        return ReportConfig.objects.filter(q).select_related("created_by")

    @staticmethod
    def report_by_id(report_id):
        return ReportConfig.objects.select_related("created_by").filter(id=report_id).first()

    @staticmethod
    def scheduled_reports():
        return ReportConfig.objects.filter(is_scheduled=True, is_active=True)

    @staticmethod
    def exports_for_report(report_id):
        return ReportExport.objects.filter(report_id=report_id).order_by("-created_at")

    @staticmethod
    def dashboards_for_user(user):
        return ReportDashboard.objects.filter(user=user, is_active=True)

    @staticmethod
    def default_dashboard(user):
        return ReportDashboard.objects.filter(user=user, is_default=True, is_active=True).first()

    @staticmethod
    def recent_exports(user, limit=10):
        return ReportExport.objects.filter(report__created_by=user).select_related("report").order_by("-created_at")[:limit]
