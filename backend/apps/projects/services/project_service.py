from django.db import transaction

from apps.core.services.audit_service import AuditService

from ..models import Project, ProjectMember
from ._events import log_created, log_updated, notify_employee, request_ip


class ProjectService:
    @staticmethod
    @transaction.atomic
    def create(*, cleaned_data, user=None, request=None):
        project = Project.objects.create(**cleaned_data)
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
        )
        return project

    @staticmethod
    @transaction.atomic
    def update(*, project, cleaned_data, user=None, request=None):
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
        return project

    @staticmethod
    @transaction.atomic
    def archive(*, project, user=None, request=None):
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
