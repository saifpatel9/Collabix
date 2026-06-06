from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.db.models import Q

from ..models import Notification, NotificationPreference


class NotificationService:
    @staticmethod
    def create_notification(
        *,
        recipient=None,
        recipient_id=None,
        title,
        message,
        notification_type=Notification.Type.INFO,
        category=Notification.Category.SYSTEM,
        action_url="",
        target=None,
        target_type="",
        target_id="",
    ):
        if recipient is None and recipient_id:
            recipient = get_user_model().objects.get(pk=recipient_id)
        preference = NotificationService.preferences_for(recipient)
        if not preference.allows(category):
            return None
        if target:
            target_type = target.__class__.__name__
            target_id = str(target.pk)
        notification = Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            category=category,
            action_url=action_url,
            target_type=target_type,
            target_id=target_id,
        )
        if preference.realtime_enabled:
            NotificationService.broadcast(notification=notification)
        return notification

    @staticmethod
    def preferences_for(user):
        preference, _ = NotificationPreference.objects.get_or_create(user=user)
        return preference

    @staticmethod
    def broadcast(*, notification):
        channel_layer = get_channel_layer()
        if not channel_layer:
            return
        async_to_sync(channel_layer.group_send)(
            f"user-notifications-{notification.recipient_id}",
            {
                "type": "notify",
                "payload": NotificationService.payload_for(notification),
            },
        )

    @staticmethod
    def payload_for(notification):
        return {
            "id": str(notification.pk),
            "title": notification.title,
            "message": notification.message,
            "notification_type": notification.notification_type,
            "category": notification.category,
            "action_url": notification.action_url,
            "is_read": notification.is_read,
            "created_at": notification.created_at.isoformat(),
            "unread_count": NotificationService.unread_count(notification.recipient),
        }

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
    def for_user(user):
        if not getattr(user, "is_authenticated", False):
            return Notification.objects.none()
        return Notification.objects.filter(recipient=user).order_by("-created_at")

    @staticmethod
    def search_and_filter(queryset, *, status=None, category=None, search=None):
        if status == "unread":
            queryset = queryset.filter(is_read=False)
        elif status == "read":
            queryset = queryset.filter(is_read=True)
        if category:
            queryset = queryset.filter(category=category)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(message__icontains=search)
            )
        return queryset.order_by("-created_at")

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
        NotificationService.broadcast_summary(user=user)
        return notification

    @staticmethod
    def mark_as_unread(*, notification, user):
        if notification.recipient_id != user.id:
            return notification
        notification.is_read = False
        notification.save(update_fields=["is_read", "updated_at"])
        NotificationService.broadcast_summary(user=user)
        return notification

    @staticmethod
    def mark_all_read(*, user):
        updated = Notification.objects.filter(recipient=user, is_read=False).update(
            is_read=True
        )
        NotificationService.broadcast_summary(user=user)
        return updated

    @staticmethod
    def broadcast_summary(*, user):
        channel_layer = get_channel_layer()
        if not channel_layer:
            return
        async_to_sync(channel_layer.group_send)(
            f"user-notifications-{user.id}",
            {
                "type": "notify",
                "payload": {
                    "event": "notification_summary",
                    "unread_count": NotificationService.unread_count(user),
                },
            },
        )
