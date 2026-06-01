from apps.core.services.activity_service import ActivityService

from ..models import TaskActivity


class TaskActivityService:
    @staticmethod
    def record(
        *,
        task,
        actor=None,
        activity_type,
        message,
        old_value=None,
        new_value=None,
        record_global=True,
    ):
        activity = TaskActivity.objects.create(
            task=task,
            actor=actor,
            activity_type=activity_type,
            message=message,
            old_value=old_value,
            new_value=new_value,
        )
        if record_global:
            ActivityService.record(
                actor=actor.user if actor else None,
                verb=message,
                target=task,
            )
        return activity
