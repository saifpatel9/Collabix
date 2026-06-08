from django.db import transaction
from django.core.exceptions import PermissionDenied, ValidationError

from apps.core.rbac.rules import can_edit_task

from ..models import TaskActivity, TaskDependency
from ._helpers import employee_for_user
from .activity_service import TaskActivityService


class TaskDependencyService:
    @staticmethod
    @transaction.atomic
    def create(
        *, successor_task, predecessor_task, dependency_type, user=None, request=None
    ):
        if not can_edit_task(user, successor_task):
            raise PermissionDenied
        if predecessor_task.project_id != successor_task.project_id:
            raise ValidationError("Dependency tasks must belong to the same project.")
        actor = employee_for_user(user)
        dependency = TaskDependency(
            successor_task=successor_task,
            predecessor_task=predecessor_task,
            dependency_type=dependency_type,
        )
        dependency.full_clean()
        dependency.save()
        TaskActivityService.record(
            task=successor_task,
            actor=actor,
            activity_type=TaskActivity.Type.DEPENDENCY_UPDATED,
            message="added task dependency",
            new_value={
                "predecessor": predecessor_task.task_code,
                "dependency_type": dependency_type,
            },
        )
        return dependency

    @staticmethod
    @transaction.atomic
    def delete(*, dependency, user=None, request=None):
        if not can_edit_task(user, dependency.successor_task):
            raise PermissionDenied
        actor = employee_for_user(user)
        task = dependency.successor_task
        old_value = {
            "predecessor": dependency.predecessor_task.task_code,
            "dependency_type": dependency.dependency_type,
        }
        dependency.delete()
        TaskActivityService.record(
            task=task,
            actor=actor,
            activity_type=TaskActivity.Type.DEPENDENCY_UPDATED,
            message="removed task dependency",
            old_value=old_value,
        )
