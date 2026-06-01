from django.db import transaction
from django.urls import reverse

from apps.notifications.services.mention_service import MentionService

from ..models import TaskActivity, TaskComment
from ._helpers import employee_for_user, notify_task_assignees
from .activity_service import TaskActivityService


class TaskCommentService:
    @staticmethod
    @transaction.atomic
    def create(*, task, cleaned_data, user=None, request=None):
        actor = employee_for_user(user)
        comment = TaskComment.objects.create(task=task, author=actor, **cleaned_data)
        TaskActivityService.record(
            task=task,
            actor=actor,
            activity_type=TaskActivity.Type.COMMENTED,
            message="commented on task",
            new_value={"comment_id": str(comment.pk)},
        )
        notify_task_assignees(
            task=task,
            title="Comment added",
            message=f"A comment was added to {task.task_code}.",
            exclude_employee=actor,
            action_url=reverse("tasks:task_detail", kwargs={"pk": task.pk}),
        )
        MentionService.notify_mentions(
            text=comment.comment,
            actor=user,
            target=task,
            action_url=reverse("tasks:task_detail", kwargs={"pk": task.pk}),
        )
        return comment
