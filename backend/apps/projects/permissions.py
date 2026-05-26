from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from apps.accounts.models import User

from .models import Project, ProjectMember


class ProjectRole:
    OWNER = "owner"
    PROJECT_MANAGER = ProjectMember.Role.PROJECT_MANAGER
    TEAM_LEAD = ProjectMember.Role.TEAM_LEAD
    CONTRIBUTOR = ProjectMember.Role.CONTRIBUTOR
    VIEWER = ProjectMember.Role.VIEWER


def user_project_role(user, project):
    if not getattr(user, "is_authenticated", False):
        return None
    if project.owner_id and project.owner.user_id == user.id:
        return ProjectRole.OWNER
    membership = project.memberships.filter(employee__user=user).first()
    return membership.role if membership else None


def can_manage_project(user, project):
    if not getattr(user, "is_authenticated", False):
        return False
    if user.is_superuser or user.role in (User.Role.ADMIN, User.Role.PROJECT_MANAGER):
        return True
    return user_project_role(user, project) in (
        ProjectRole.OWNER,
        ProjectRole.PROJECT_MANAGER,
        ProjectRole.TEAM_LEAD,
    )


def can_view_project(user, project):
    if can_manage_project(user, project):
        return True
    return user_project_role(user, project) in (
        ProjectRole.CONTRIBUTOR,
        ProjectRole.VIEWER,
    )


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
            return super(ProjectAccessMixin, self).dispatch(request, *args, **kwargs)
        self.project_object = self.get_project_object()
        if not can_manage_project(request.user, self.project_object):
            raise PermissionDenied
        return super(ProjectAccessMixin, self).dispatch(request, *args, **kwargs)
