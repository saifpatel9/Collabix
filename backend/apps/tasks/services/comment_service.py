from django.db import transaction

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
        )
        return comment
