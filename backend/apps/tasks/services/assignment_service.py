from django.db import transaction
from django.urls import reverse

from apps.notifications.models import Notification

from ..models import TaskActivity, TaskAssignment
from ._helpers import audit_update, employee_for_user, notify_employee
from .activity_service import TaskActivityService


class TaskAssignmentService:
    @staticmethod
    @transaction.atomic
    def assign(*, task, employee, user=None, request=None):
        actor = employee_for_user(user)
        was_assigned = task.assignments.exists()
        assignment = TaskAssignment.objects.create(
            task=task, employee=employee, assigned_by=actor
        )
        audit_update(
            user=user,
            instance=task,
            old_data=None,
            new_data={"assigned_employee_id": str(employee.pk)},
            request=request,
        )
        TaskActivityService.record(
            task=task,
            actor=actor,
            activity_type=TaskActivity.Type.ASSIGNED,
            message="assigned task",
            new_value={"employee": employee.user.full_name},
        )
        notify_employee(
            employee=employee,
            title="Task reassigned" if was_assigned else "Task assigned",
            message=f"You were assigned to {task.task_code}: {task.title}.",
            notification_type=Notification.Type.INFO,
            category=Notification.Category.TASK,
            action_url=reverse("tasks:task_detail", kwargs={"pk": task.pk}),
            target=task,
        )
        return assignment
