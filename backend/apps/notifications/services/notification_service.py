from ..models import Notification


class NotificationService:
    @staticmethod
    def create_notification(
        *, recipient, title, message, notification_type=Notification.Type.INFO
    ):
        return Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
        )

    @staticmethod
    def unread_for(user):
        return Notification.objects.filter(recipient=user, is_read=False).order_by(
            "-created_at"
        )

    @staticmethod
    def recent_for(user, limit=8):
        return Notification.objects.filter(recipient=user).order_by("-created_at")[
            :limit
        ]

    @staticmethod
    def unread_count(user):
        if not getattr(user, "is_authenticated", False):
            return 0
        return Notification.objects.filter(recipient=user, is_read=False).count()

    @staticmethod
    def mark_as_read(*, notification, user):
        if notification.recipient_id != user.id:
            return notification
        notification.is_read = True
        notification.save(update_fields=["is_read", "updated_at"])
        return notification

    @staticmethod
    def mark_all_read(*, user):
        return Notification.objects.filter(recipient=user, is_read=False).update(
            is_read=True
        )
