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
    is_read = models.BooleanField(default=False)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["recipient", "is_read"], name="notif_recipient_read_idx"
            ),
            models.Index(fields=["notification_type"], name="notif_type_idx"),
        ]

    def __str__(self) -> str:
        return self.title
