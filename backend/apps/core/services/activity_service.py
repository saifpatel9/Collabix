from apps.core.models import Activity


class ActivityService:
    @staticmethod
    def record(*, actor, verb, target):
        return Activity.objects.create(
            actor=actor if getattr(actor, "is_authenticated", False) else None,
            verb=verb,
            target_type=target.__class__.__name__,
            target_id=str(target.pk),
        )

    @staticmethod
    def recent(limit=10):
        return Activity.objects.select_related("actor").order_by("-timestamp")[:limit]
