from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from apps.core.rbac.rules import can_edit_task, can_execute_task, can_view_task

from .models import Task

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
