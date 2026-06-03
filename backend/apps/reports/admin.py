from django.contrib import admin

from apps.reports.models import ReportConfig, ReportDashboard, ReportExport


@admin.register(ReportConfig)
class ReportConfigAdmin(admin.ModelAdmin):
    list_display = ["name", "report_type", "created_by", "is_scheduled", "frequency", "last_generated", "is_active"]
    list_filter = ["report_type", "is_scheduled", "frequency", "is_active"]
    search_fields = ["name", "description"]
    date_hierarchy = "created_at"


@admin.register(ReportExport)
class ReportExportAdmin(admin.ModelAdmin):
    list_display = ["report", "export_format", "status", "file_size", "completed_at"]
    list_filter = ["export_format", "status"]
    date_hierarchy = "created_at"


@admin.register(ReportDashboard)
class ReportDashboardAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "is_default", "is_active"]
    list_filter = ["is_default", "is_active"]
