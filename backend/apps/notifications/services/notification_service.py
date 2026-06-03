from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from ..models import Notification


class NotificationService:
    @staticmethod
    def create_notification(
        *, recipient, title, message, notification_type=Notification.Type.INFO, link="",
        category=None, action_url="", target=None,
    ):
        kwargs = {
            "recipient": recipient,
            "title": title,
            "message": message,
            "notification_type": notification_type,
            "link": link,
            "action_url": action_url,
        }
        if category:
            kwargs["category"] = category
        if target is not None:
            kwargs["target_id"] = str(getattr(target, "id", ""))
            kwargs["target_type"] = target.__class__.__name__
        notification = Notification.objects.create(**kwargs)
        NotificationService._push_realtime(notification)
        return notification

    @staticmethod
    def _push_realtime(notification):
        try:
            channel_layer = get_channel_layer()
            group_name = f"user-notifications-{notification.recipient_id}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "notify",
                    "payload": {
                        "id": str(notification.id),
                        "title": notification.title,
                        "message": notification.message,
                        "type": notification.notification_type,
                        "link": notification.link,
                        "created_at": timezone.localtime(notification.created_at).isoformat(),
                        "is_read": notification.is_read,
                    },
                },
            )
        except Exception:
            pass

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
