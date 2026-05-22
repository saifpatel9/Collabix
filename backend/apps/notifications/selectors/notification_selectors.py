from ..models import Notification


class NotificationSelector:
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
