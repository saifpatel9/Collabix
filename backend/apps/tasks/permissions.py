from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from apps.accounts.models import User
from apps.projects.models import ProjectMember
from apps.projects.permissions import can_manage_project, can_view_project

from .models import Task


def is_task_owner(user, task):
    return (
        getattr(user, "is_authenticated", False) and task.created_by.user_id == user.id
    )


def is_task_assignee(user, task):
    return (
        getattr(user, "is_authenticated", False)
        and task.assignments.filter(employee__user=user).exists()
    )


def is_project_team_lead(user, task):
    return (
        getattr(user, "is_authenticated", False)
        and task.project.memberships.filter(
            employee__user=user, role=ProjectMember.Role.TEAM_LEAD
        ).exists()
    )


def has_task_admin_role(user):
    return getattr(user, "is_authenticated", False) and (
        user.is_superuser
        or user.role
        in (
            User.Role.ADMIN,
            User.Role.DEPARTMENT_ADMIN,
            User.Role.HR_MANAGER,
            User.Role.PROJECT_MANAGER,
        )
    )


def can_view_task(user, task):
    return (
        has_task_admin_role(user)
        or is_task_owner(user, task)
        or is_task_assignee(user, task)
        or can_view_project(user, task.project)
    )


def can_edit_task(user, task):
    return (
        has_task_admin_role(user)
        or is_task_owner(user, task)
        or is_project_team_lead(user, task)
        or can_manage_project(user, task.project)
    )


def can_execute_task(user, task):
    return can_edit_task(user, task) or is_task_assignee(user, task)


class TaskAccessMixin(LoginRequiredMixin):
    task_object = None
    task_kwarg = "pk"

    def get_task_object(self):
        return get_object_or_404(
            Task.objects.select_related(
                "project", "project__owner__user", "created_by__user"
            ).prefetch_related("assignments__employee__user", "project__memberships"),
            pk=self.kwargs[self.task_kwarg],
        )

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.task_object = self.get_task_object()
        if not can_view_task(request.user, self.task_object):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class TaskManageMixin(TaskAccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super(TaskAccessMixin, self).dispatch(request, *args, **kwargs)
        self.task_object = self.get_task_object()
        if not can_edit_task(request.user, self.task_object):
            raise PermissionDenied
        return super(TaskAccessMixin, self).dispatch(request, *args, **kwargs)


class TaskExecuteMixin(TaskAccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super(TaskAccessMixin, self).dispatch(request, *args, **kwargs)
        self.task_object = self.get_task_object()
        if not can_execute_task(request.user, self.task_object):
            raise PermissionDenied
        return super(TaskAccessMixin, self).dispatch(request, *args, **kwargs)
