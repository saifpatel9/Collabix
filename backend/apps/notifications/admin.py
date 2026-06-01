from django.contrib import admin

from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "recipient",
        "notification_type",
        "category",
        "is_read",
        "created_at",
    )
    list_filter = ("notification_type", "category", "is_read")
    search_fields = ("title", "message", "recipient__full_name", "recipient__email")
    readonly_fields = ("created_at", "updated_at")


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "task_notifications",
        "project_notifications",
        "mention_notifications",
        "realtime_enabled",
    )
    search_fields = ("user__full_name", "user__email")
