import re

from django.contrib.auth import get_user_model

from ..models import Notification
from .notification_service import NotificationService

MENTION_RE = re.compile(r"@([A-Za-z0-9_.-]+)")


class MentionService:
    @staticmethod
    def mentioned_users(text):
        tokens = {match.lower() for match in MENTION_RE.findall(text or "")}
        if not tokens:
            return []
        User = get_user_model()
        users = []
        for user in User.objects.filter(is_active=True):
            aliases = {user.email.split("@", 1)[0].lower()}
            aliases.add(user.full_name.lower().replace(" ", "."))
            aliases.add(user.full_name.lower().replace(" ", ""))
            if aliases & tokens:
                users.append(user)
        return users

    @staticmethod
    def notify_mentions(*, text, actor=None, target, action_url):
        actor_name = getattr(actor, "full_name", None) or getattr(
            actor, "email", "Someone"
        )
        for user in MentionService.mentioned_users(text):
            if actor and user.pk == actor.pk:
                continue
            NotificationService.create_notification(
                recipient=user,
                title="You were mentioned",
                message=f"{actor_name} mentioned you.",
                notification_type=Notification.Type.INFO,
                category=Notification.Category.MENTION,
                action_url=action_url,
                target=target,
            )
