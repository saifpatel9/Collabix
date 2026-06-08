from django.db import transaction
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from apps.notifications.models import Notification
from apps.core.rbac.rules import can_execute_task

from ..models import TaskActivity, TaskChecklist, TaskChecklistItem
from ._helpers import employee_for_user, notify_task_assignees
from .activity_service import TaskActivityService


class TaskChecklistService:
    @staticmethod
    @transaction.atomic
    def create_checklist(*, task, cleaned_data, user=None, request=None):
        if not can_execute_task(user, task):
            raise PermissionDenied
        actor = employee_for_user(user)
        checklist = TaskChecklist.objects.create(task=task, **cleaned_data)
        TaskActivityService.record(
            task=task,
            actor=actor,
            activity_type=TaskActivity.Type.CHECKLIST_UPDATED,
            message="created task checklist",
            new_value={"checklist": checklist.title},
        )
        return checklist

    @staticmethod
    @transaction.atomic
    def create_item(*, checklist, cleaned_data, user=None, request=None):
        if not can_execute_task(user, checklist.task):
            raise PermissionDenied
        actor = employee_for_user(user)
        item = TaskChecklistItem.objects.create(checklist=checklist, **cleaned_data)
        TaskActivityService.record(
            task=checklist.task,
            actor=actor,
            activity_type=TaskActivity.Type.CHECKLIST_UPDATED,
            message="added checklist item",
            new_value={"item": item.title},
        )
        return item

    @staticmethod
    @transaction.atomic
    def toggle_item(*, item, is_completed, user=None, request=None):
        if not can_execute_task(user, item.checklist.task):
            raise PermissionDenied
        actor = employee_for_user(user)
        item.is_completed = is_completed
        item.completed_by = actor if is_completed else None
        item.completed_at = timezone.now() if is_completed else None
        item.full_clean()
        item.save(
            update_fields=["is_completed", "completed_by", "completed_at", "updated_at"]
        )
        task = item.checklist.task
        TaskActivityService.record(
            task=task,
            actor=actor,
            activity_type=TaskActivity.Type.CHECKLIST_UPDATED,
            message="updated checklist item",
            new_value={"item": item.title, "is_completed": item.is_completed},
        )
        progress = task.checklist_progress
        if progress["total"] and progress["total"] == progress["completed"]:
            notify_task_assignees(
                task=task,
                title="Checklist completed",
                message=f"All checklist items are completed for {task.task_code}.",
                notification_type=Notification.Type.SUCCESS,
            )
        return item
