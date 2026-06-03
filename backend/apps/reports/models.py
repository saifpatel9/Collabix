import uuid

from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class ReportConfig(BaseModel):
    REPORT_TYPES = [
        ("performance", "Employee Performance"),
        ("productivity", "Team Productivity"),
        ("project", "Project Progress"),
        ("task", "Task Analytics"),
        ("attendance", "Attendance Analytics"),
        ("workflow", "Workflow Efficiency"),
    ]

    FREQUENCY_CHOICES = [
        ("once", "One-time"),
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
    ]

    FORMAT_CHOICES = [
        ("pdf", "PDF"),
        ("xlsx", "Excel (XLSX)"),
        ("csv", "CSV"),
    ]

    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="report_configs",
    )
    filters = models.JSONField(default=dict, blank=True)
    is_scheduled = models.BooleanField(default=False)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, blank=True, default="once")
    export_format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default="csv")
    recipients = models.JSONField(default=list, blank=True)
    last_generated = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "report_configs"
        ordering = ["-created_at"]
        verbose_name = "Report Configuration"
        verbose_name_plural = "Report Configurations"

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.name}"


class ReportExport(BaseModel):
    report = models.ForeignKey(
        ReportConfig,
        on_delete=models.CASCADE,
        related_name="exports",
    )
    export_format = models.CharField(max_length=10, choices=ReportConfig.FORMAT_CHOICES)
    file = models.FileField(upload_to="reports/exports/%Y/%m/", blank=True, null=True)
    file_size = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("completed", "Completed"),
            ("failed", "Failed"),
        ],
        default="pending",
    )
    error_message = models.TextField(blank=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "report_exports"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.report.name} - {self.get_export_format_display()}"


class ReportDashboard(BaseModel):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="dashboards",
    )
    layout = models.JSONField(default=dict, blank=True)
    widgets = models.JSONField(default=list, blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "report_dashboards"
        ordering = ["name"]

    def __str__(self):
        return self.name


class AnalyticsSnapshot(BaseModel):
    CACHE_KEY_PREFIX = "analytics_snapshot"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="analytics_snapshots",
    )
    snapshot_type = models.CharField(
        max_length=30,
        choices=ReportConfig.REPORT_TYPES + [("dashboard", "Dashboard Overview")],
    )
    data = models.JSONField(default=dict)
    filters = models.JSONField(default=dict, blank=True)
    cached_at = models.DateTimeField(auto_now=True)
    ttl_seconds = models.PositiveIntegerField(default=300)

    class Meta:
        db_table = "analytics_snapshots"
        indexes = [
            models.Index(fields=["user", "snapshot_type", "cached_at"]),
        ]
        verbose_name = "Analytics Snapshot"
        verbose_name_plural = "Analytics Snapshots"

    def __str__(self):
        return f"{self.user} - {self.snapshot_type}"
