from django.urls import path

from .views import AuditTimelineView, GlobalSearchView, RecentActivityPartialView

app_name = "core"

urlpatterns = [
    path("search/", GlobalSearchView.as_view(), name="global_search"),
    path(
        "activity/recent/", RecentActivityPartialView.as_view(), name="recent_activity"
    ),
    path("audit/timeline/", AuditTimelineView.as_view(), name="audit_timeline"),
]
