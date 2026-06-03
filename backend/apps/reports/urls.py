from django.urls import path

from apps.reports import views

app_name = "reports"

urlpatterns = [
    # Analytics Pages
    path("analytics/", views.AnalyticsDashboardView.as_view(), name="analytics_dashboard"),
    path("analytics/performance/", views.PerformanceAnalyticsView.as_view(), name="analytics_performance"),
    path("analytics/productivity/", views.ProductivityAnalyticsView.as_view(), name="analytics_productivity"),
    path("analytics/projects/", views.ProjectAnalyticsView.as_view(), name="analytics_projects"),
    path("analytics/tasks/", views.TaskAnalyticsView.as_view(), name="analytics_tasks"),
    path("analytics/attendance/", views.AttendanceAnalyticsView.as_view(), name="analytics_attendance"),
    path("analytics/workflow/", views.WorkflowAnalyticsView.as_view(), name="analytics_workflow"),
    # Report CRUD
    path("reports/", views.ReportListView.as_view(), name="report_list"),
    path("reports/create/", views.ReportCreateView.as_view(), name="report_create"),
    path("reports/<uuid:pk>/", views.ReportDetailView.as_view(), name="report_detail"),
    path("reports/<uuid:pk>/edit/", views.ReportUpdateView.as_view(), name="report_update"),
    path("reports/<uuid:pk>/delete/", views.ReportDeleteView.as_view(), name="report_delete"),
    path("reports/<uuid:pk>/generate/", views.ReportGenerateView.as_view(), name="report_generate"),
    path("reports/<uuid:pk>/export/<str:export_format>/", views.ReportExportView.as_view(), name="report_export"),
    path("reports/<uuid:pk>/schedule/", views.ReportScheduleView.as_view(), name="report_schedule"),
    # API / HTMX endpoints
    path("analytics/api/kpis/", views.KpiDataView.as_view(), name="api_kpis"),
    path("analytics/api/chart-data/", views.ChartDataView.as_view(), name="api_chart_data"),
    path("analytics/api/tasks-by-priority/", views.TasksByPriorityView.as_view(), name="api_tasks_by_priority"),
    path("analytics/api/workload/", views.WorkloadDataView.as_view(), name="api_workload"),
]
