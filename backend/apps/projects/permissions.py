from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404

from apps.core.rbac.rules import (
    ProjectRole,
    can_manage_milestone,
    can_manage_project,
    can_view_project,
    user_project_role,
)

from .models import Project, ProjectMember

class ProjectAccessMixin(LoginRequiredMixin):
    project_kwarg = "project_pk"
    project_object = None

    def get_project_object(self):
        lookup = self.kwargs.get(self.project_kwarg) or self.kwargs.get("pk")
        return get_object_or_404(
            Project.objects.select_related("owner__user", "department", "team"),
            pk=lookup,
        )

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.project_object = self.get_project_object()
        if not can_view_project(request.user, self.project_object):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ProjectManageMixin(ProjectAccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        self.project_object = self.get_project_object()
        if not self.project_object:
            raise Http404("Project not found")

        if not can_manage_project(request.user, self.project_object):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


class MilestoneManageMixin(ProjectAccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        self.project_object = self.get_project_object()
        if not self.project_object:
            raise Http404("Project not found")

        if not can_manage_milestone(request.user, self.project_object):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)
