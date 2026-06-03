from django.conf import settings
from django.db import models

from apps.core.models import BaseModel


class NotificationBaseModel(BaseModel):
    class Meta:
        abstract = True


class Notification(NotificationBaseModel):
    class Type(models.TextChoices):
        INFO = "info", "Info"
        SUCCESS = "success", "Success"
        WARNING = "warning", "Warning"
        ERROR = "error", "Error"
        APPROVAL = "approval", "Approval"
        SYSTEM = "system", "System"

    class Category(models.TextChoices):
        TASK = "task", "Task"
        PROJECT = "project", "Project"
        MENTION = "mention", "Mention"
        APPROVAL = "approval", "Approval"
        SYSTEM = "system", "System"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title = models.CharField(max_length=150)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.INFO,
    )
    category = models.CharField(
        max_length=30, choices=Category.choices, default=Category.SYSTEM
    )
    link = models.CharField(max_length=500, blank=True, default="")
    action_url = models.CharField(max_length=500, blank=True)
    target_type = models.CharField(max_length=150, blank=True)
    target_id = models.CharField(max_length=64, blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["recipient", "is_read"], name="notif_recipient_read_idx"
            ),
            models.Index(fields=["notification_type"], name="notif_type_idx"),
            models.Index(fields=["category"], name="notif_category_idx"),
            models.Index(
                fields=["target_type", "target_id"], name="notif_target_idx"
            ),
        ]

    def __str__(self) -> str:
        return self.title


class NotificationPreference(NotificationBaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preference",
    )
    task_notifications = models.BooleanField(default=True)
    project_notifications = models.BooleanField(default=True)
    mention_notifications = models.BooleanField(default=True)
    approval_notifications = models.BooleanField(default=True)
    system_notifications = models.BooleanField(default=True)
    realtime_enabled = models.BooleanField(default=True)

    class Meta:
        db_table = "notification_preferences"

    def __str__(self) -> str:
        return f"{self.user} preferences"
