from django.urls import path

from .views import (
    NotificationDropdownView,
    NotificationMarkAllReadView,
    NotificationMarkReadView,
)

app_name = "notifications"

urlpatterns = [
    path("dropdown/", NotificationDropdownView.as_view(), name="dropdown"),
    path("<uuid:pk>/read/", NotificationMarkReadView.as_view(), name="mark_read"),
    path("read-all/", NotificationMarkAllReadView.as_view(), name="mark_all_read"),
]
