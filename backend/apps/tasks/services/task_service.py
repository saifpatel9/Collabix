from datetime import timedelta

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from apps.core.rbac.permissions import is_authenticated
from apps.core.rbac.rules import can_edit_task, can_execute_task, can_view_project

from ..models import Task, TaskActivity, TaskDependency
from ._helpers import (
    audit_create,
    audit_delete,
    audit_update,
    employee_for_user,
    notify_task_assignees,
)
from .activity_service import TaskActivityService


def validate_dependencies(task, new_status):
    dependencies = task.predecessor_dependencies.select_related("predecessor_task")

    for dep in dependencies:
        predecessor = dep.predecessor_task

        if dep.dependency_type == TaskDependency.Type.START_TO_START:
            if new_status == Task.Status.IN_PROGRESS:
                if predecessor.status not in (
                    Task.Status.IN_PROGRESS,
                    Task.Status.COMPLETED,
                ):
                    raise ValidationError(
                        f"Task cannot start until {predecessor.task_code} has started."
                    )

        elif dep.dependency_type in (
            TaskDependency.Type.FINISH_TO_START,
            TaskDependency.Type.FINISH_TO_FINISH,
        ):
            if new_status == Task.Status.COMPLETED:
                if predecessor.status != Task.Status.COMPLETED:
                    raise ValidationError(
                        f"Task cannot complete until {predecessor.task_code} is completed."
                    )

class TaskService:
    @staticmethod
    def _ensure_can_create(*, user, cleaned_data):
        project = cleaned_data.get("project")

        if project and not can_view_project(user, project):
            raise PermissionDenied

    @staticmethod
    def _ensure_can_update(*, user, task, cleaned_data):
        keys = set(cleaned_data.keys())
        
        if keys == {"status"}:
            allowed = can_execute_task(user, task)
        else:
            allowed = can_edit_task(user, task)
        if not allowed:
            raise PermissionDenied

    @staticmethod
    @transaction.atomic
    def create(*, cleaned_data, user=None, request=None):
        TaskService._ensure_can_create(user=user, cleaned_data=cleaned_data)
        actor = employee_for_user(user)
        task = Task(
            created_by=actor,
            updated_by=actor,
            **cleaned_data)
        task.full_clean()
        task.save()
        audit_create(
            user=user,
            instance=task,
            data={"task_code": task.task_code, "title": task.title},
            request=request,
        )
        TaskActivityService.record(
            task=task,
            actor=actor,
            activity_type=TaskActivity.Type.CREATED,
            message="created task",
            new_value={"task_code": task.task_code, "title": task.title},
        )
        return task

    @staticmethod
    @transaction.atomic
    def update(*, task, cleaned_data, user=None, request=None):
        TaskService._ensure_can_update(user=user, task=task, cleaned_data=cleaned_data)
        actor = employee_for_user(user)
        
        # Check if we're changing status
        new_status = cleaned_data.get("status")
        if new_status is not None and new_status != task.status:
            validate_dependencies(task, new_status)
            
        old_data = {
            "title": task.title,
            "status": task.status,
            "priority": task.priority,
            "due_date": str(task.due_date) if task.due_date else None,
            "is_archived": task.is_archived,
        }
        old_status = task.status
        old_priority = task.priority
        old_due_date = task.due_date
        for field, value in cleaned_data.items():
            setattr(task, field, value)
        task.updated_by = actor
        task.full_clean()
        task.save()
        new_data = {
            "title": task.title,
            "status": task.status,
            "priority": task.priority,
            "due_date": str(task.due_date) if task.due_date else None,
            "is_archived": task.is_archived,
        }
        audit_update(
            user=user,
            instance=task,
            old_data=old_data,
            new_data=new_data,
            request=request,
        )
        TaskActivityService.record(
            task=task,
            actor=actor,
            activity_type=TaskActivity.Type.UPDATED,
            message="updated task",
            old_value=old_data,
            new_value=new_data,
        )
        if old_status != task.status:
            TaskActivityService.record(
                task=task,
                actor=actor,
                activity_type=TaskActivity.Type.STATUS_CHANGED,
                message="changed task status",
                old_value={"status": old_status},
                new_value={"status": task.status},
            )
            if task.status == Task.Status.COMPLETED:
                notify_task_assignees(
                    task=task,
                    title="Task completed",
                    message=f"{task.task_code} was marked completed.",
                    exclude_employee=actor,
                    action_url=reverse("tasks:task_detail", kwargs={"pk": task.pk}),
                )
        if old_priority != task.priority:
            TaskActivityService.record(
                task=task,
                actor=actor,
                activity_type=TaskActivity.Type.PRIORITY_CHANGED,
                message="changed task priority",
                old_value={"priority": old_priority},
                new_value={"priority": task.priority},
            )
        if old_due_date != task.due_date:
            TaskActivityService.record(
                task=task,
                actor=actor,
                activity_type=TaskActivity.Type.DUE_DATE_CHANGED,
                message="changed task due date",
                old_value={"due_date": str(old_due_date) if old_due_date else None},
                new_value={"due_date": str(task.due_date) if task.due_date else None},
            )
        return task

    @staticmethod
    def change_status(*, task, status, user=None, request=None):
        return TaskService.update(
            task=task, cleaned_data={"status": status}, user=user, request=request
        )

    @staticmethod
    def change_priority(*, task, priority, user=None, request=None):
        return TaskService.update(
            task=task, cleaned_data={"priority": priority}, user=user, request=request
        )

    @staticmethod
    @transaction.atomic
    def archive(*, task, user=None, request=None):
        return TaskService.update(
            task=task, cleaned_data={"is_archived": True}, user=user, request=request
        )

    @staticmethod
    @transaction.atomic
    def delete(*, task, user=None, request=None):
        if not can_edit_task(user, task):
            raise PermissionDenied
        old_data = {"task_code": task.task_code, "title": task.title}
        audit_delete(user=user, instance=task, old_data=old_data, request=request)
        task.delete()

    @staticmethod
    def notify_due_soon(*, days=1):
        target_date = timezone.localdate() + timedelta(days=days)
        queryset = Task.objects.filter(
            due_date=target_date,
            is_archived=False,
            status__in=[
                Task.Status.BACKLOG,
                Task.Status.TODO,
                Task.Status.IN_PROGRESS,
                Task.Status.REVIEW,
                Task.Status.BLOCKED,
            ],
        ).prefetch_related("assignments__employee__user")
        for task in queryset:
            notify_task_assignees(
                task=task,
                title="Task due soon",
                message=f"{task.task_code} is due on {task.due_date}.",
                action_url=reverse("tasks:task_detail", kwargs={"pk": task.pk}),
            )
        return queryset.count()

    @staticmethod
    def notify_overdue():
        queryset = Task.objects.filter(
            due_date__lt=timezone.localdate(),
            is_archived=False,
            status__in=[
                Task.Status.BACKLOG,
                Task.Status.TODO,
                Task.Status.IN_PROGRESS,
                Task.Status.REVIEW,
                Task.Status.BLOCKED,
            ],
        ).prefetch_related("assignments__employee__user")
        for task in queryset:
            notify_task_assignees(
                task=task,
                title="Task overdue",
                message=f"{task.task_code} is overdue.",
                action_url=reverse("tasks:task_detail", kwargs={"pk": task.pk}),
            )
        return queryset.count()
