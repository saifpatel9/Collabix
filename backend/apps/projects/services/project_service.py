from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from apps.accounts.models import User
from apps.core.rbac.policies import can_create_project
from apps.core.rbac.rules import can_manage_project
from apps.core.services.audit_service import AuditService

from ..models import Project, ProjectMember
from ._events import (
    log_created,
    log_updated,
    notify_employee,
    notify_project_members,
    request_ip,
)


class ProjectService:
    @staticmethod
    @transaction.atomic
    def create(*, cleaned_data, user=None, request=None):
        # RBAC check BEFORE creation
        if not can_create_project(user):
            raise PermissionDenied

        project = Project.objects.create(**cleaned_data)

        # 3. Ensure owner is project manager
        ProjectMember.objects.get_or_create(
            project=project,
            employee=project.owner,
            defaults={"role": ProjectMember.Role.PROJECT_MANAGER},
        )

        log_created(
            user=user,
            instance=project,
            data={"name": project.name, "code": project.code},
            request=request,
            verb="created project",
        )

        notify_employee(
            employee=project.owner,
            title="Project created",
            message=f"{project.name} was created with you as owner.",
            action_url=reverse("projects:project_detail", kwargs={"pk": project.pk}),
            target=project,
        )

        return project

    @staticmethod
    @transaction.atomic
    def update(*, project, cleaned_data, user=None, request=None):
        if not can_manage_project(user, project):
            raise PermissionDenied
        old_status = project.status
        old_data = {
            "name": project.name,
            "status": project.status,
            "priority": project.priority,
            "is_archived": project.is_archived,
        }
        for field, value in cleaned_data.items():
            setattr(project, field, value)
        project.full_clean()
        project.save()
        if project.owner:
            ProjectMember.objects.update_or_create(
                project=project,
                employee=project.owner,
                defaults={"role": ProjectMember.Role.PROJECT_MANAGER},
            )
        if old_status != project.status:
            AuditService.log_status_change(
                user=user,
                instance=project,
                old_status=old_status,
                new_status=project.status,
                ip_address=request_ip(request),
            )
            verb = "changed project status"
        else:
            verb = "updated project"
        log_updated(
            user=user,
            instance=project,
            old_data=old_data,
            new_data={
                "name": project.name,
                "status": project.status,
                "priority": project.priority,
                "is_archived": project.is_archived,
            },
            request=request,
            verb=verb,
        )
        notify_project_members(
            project=project,
            title="Project updated",
            message=f"{project.name} was updated.",
            action_url=reverse("projects:project_detail", kwargs={"pk": project.pk}),
            exclude_user=user,
            target=project,
        )
        return project

    @staticmethod
    @transaction.atomic
    def archive(*, project, user=None, request=None):
        if not can_manage_project(user, project):
            raise PermissionDenied
        old_data = {"is_archived": project.is_archived}
        project.is_archived = True
        project.save(update_fields=["is_archived", "updated_at"])
        log_updated(
            user=user,
            instance=project,
            old_data=old_data,
            new_data={"is_archived": True},
            request=request,
            verb="archived project",
        )
        return project
