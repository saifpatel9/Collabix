from django.urls import path

from .views import (
    NotificationCenterView,
    NotificationDropdownView,
    NotificationMarkAllReadView,
    NotificationMarkReadView,
    NotificationPreferenceView,
)

app_name = "notifications"

urlpatterns = [
    path("", NotificationCenterView.as_view(), name="center"),
    path("dropdown/", NotificationDropdownView.as_view(), name="dropdown"),
    path("preferences/", NotificationPreferenceView.as_view(), name="preferences"),
    path("<uuid:pk>/read/", NotificationMarkReadView.as_view(), name="mark_read"),
    path("read-all/", NotificationMarkAllReadView.as_view(), name="mark_all_read"),
]
