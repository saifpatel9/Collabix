import csv
import io
from datetime import datetime, timedelta

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone

from apps.core.services.audit_service import AuditService
from apps.notifications.services.notification_service import NotificationService
from apps.reports.models import ReportConfig, ReportDashboard, ReportExport


class ReportService:
    """Business logic for managing reports."""

    @staticmethod
    def create_report(name, report_type, created_by, filters=None, description="", **kwargs):
        report = ReportConfig.objects.create(
            name=name,
            report_type=report_type,
            created_by=created_by,
            filters=filters or {},
            description=description,
            **kwargs,
        )
        AuditService.log_create(created_by, report, "Created report configuration")
        return report

    @staticmethod
    def update_report(report_id, data):
        report = ReportConfig.objects.filter(id=report_id).first()
        if not report:
            return None
        for key, value in data.items():
            setattr(report, key, value)
        report.save()
        AuditService.log_update(report.created_by, report, "Updated report configuration")
        return report

    @staticmethod
    def delete_report(report_id):
        report = ReportConfig.objects.filter(id=report_id).first()
        if report:
            AuditService.log_delete(report.created_by, report, "Deleted report configuration")
            report.delete()
            return True
        return False

    @staticmethod
    def generate_report(report):
        """Queue report generation and create export record."""
        export = ReportExport.objects.create(
            report=report,
            export_format=report.export_format,
            status="processing",
        )
        try:
            from apps.reports.services.export_service import ExportService

            file_content, file_name = ExportService.generate(report, report.export_format)
            export.file.save(file_name, ContentFile(file_content))
            export.status = "completed"
            export.file_size = export.file.size
            export.completed_at = timezone.now()
            export.expires_at = timezone.now() + timedelta(days=7)
            export.save()

            report.last_generated = timezone.now()
            report.save()

            NotificationService.create_notification(
                user=report.created_by,
                title="Report Ready",
                message=f'Your report "{report.name}" is ready for download.',
                notification_type="report_ready",
                related_object_id=str(report.id),
            )
        except Exception as e:
            export.status = "failed"
            export.error_message = str(e)
            export.save()
        return export

    @staticmethod
    def schedule_report(report_id, frequency, export_format="csv", recipients=None):
        report = ReportConfig.objects.filter(id=report_id).first()
        if not report:
            return None
        report.is_scheduled = True
        report.frequency = frequency
        report.export_format = export_format
        if recipients:
            report.recipients = recipients
        report.save()
        AuditService.log_update(report.created_by, report, f"Scheduled report: {frequency}")
        return report

    @staticmethod
    def unschedule_report(report_id):
        report = ReportConfig.objects.filter(id=report_id).first()
        if not report:
            return None
        report.is_scheduled = False
        report.frequency = "once"
        report.save()
        return report


class ReportDashboardService:
    """Business logic for report dashboards."""

    @staticmethod
    def create_dashboard(name, user, layout=None, widgets=None):
        dashboard = ReportDashboard.objects.create(
            name=name,
            user=user,
            layout=layout or {},
            widgets=widgets or [],
        )
        return dashboard

    @staticmethod
    def update_dashboard(dashboard_id, data):
        dashboard = ReportDashboard.objects.filter(id=dashboard_id).first()
        if not dashboard:
            return None
        for key, value in data.items():
            setattr(dashboard, key, value)
        dashboard.save()
        return dashboard

    @staticmethod
    def set_default(dashboard_id, user):
        ReportDashboard.objects.filter(user=user).update(is_default=False)
        ReportDashboard.objects.filter(id=dashboard_id, user=user).update(is_default=True)
