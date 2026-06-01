from django.db import transaction

from ..models import TaskActivity, TaskDependency
from ._helpers import employee_for_user
from .activity_service import TaskActivityService


class TaskDependencyService:
    @staticmethod
    @transaction.atomic
    def create(
        *, successor_task, predecessor_task, dependency_type, user=None, request=None
    ):
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
