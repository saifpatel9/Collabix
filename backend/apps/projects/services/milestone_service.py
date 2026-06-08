from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from apps.core.rbac.rules import can_manage_milestone
from apps.core.services.audit_service import AuditService
from apps.notifications.models import Notification

from ..models import Milestone
from ._events import (
    log_created,
    log_deleted,
    log_updated,
    notify_project_members,
    request_ip,
)


class MilestoneService:
    @staticmethod
    @transaction.atomic
    def create(*, project, cleaned_data, user=None, request=None):
        if not can_manage_milestone(user, project):
            raise PermissionDenied
        milestone = Milestone.objects.create(project=project, **cleaned_data)
        log_created(
            user=user,
            instance=milestone,
            data={"project": str(project.pk), "name": milestone.name},
            request=request,
            verb="created milestone",
        )
        notify_project_members(
            project=project,
            title="Milestone created",
            message=f"{milestone.name} was added to {project.name}.",
            action_url=reverse("projects:project_detail", kwargs={"pk": project.pk}),
            exclude_user=user,
            target=milestone,
        )
        return milestone

    @staticmethod
    @transaction.atomic
    def update(*, milestone, cleaned_data, user=None, request=None):
        if not can_manage_milestone(user, milestone.project):
            raise PermissionDenied
        old_status = milestone.status
        old_data = {"name": milestone.name, "status": milestone.status}
        for field, value in cleaned_data.items():
            setattr(milestone, field, value)
        milestone.save()
        if old_status != milestone.status:
            AuditService.log_status_change(
                user=user,
                instance=milestone,
                old_status=old_status,
                new_status=milestone.status,
                ip_address=request_ip(request),
            )
            verb = "changed milestone status"
        else:
            verb = "updated milestone"
        log_updated(
            user=user,
            instance=milestone,
            old_data=old_data,
            new_data={"name": milestone.name, "status": milestone.status},
            request=request,
            verb=verb,
        )
        if (
            old_status != milestone.status
            and milestone.status == Milestone.Status.COMPLETED
        ):
            notify_project_members(
                project=milestone.project,
                title="Milestone completed",
                message=f"{milestone.name} was completed.",
                notification_type=Notification.Type.SUCCESS,
                action_url=reverse(
                    "projects:project_detail", kwargs={"pk": milestone.project.pk}
                ),
                exclude_user=user,
                target=milestone,
            )
        return milestone

    @staticmethod
    @transaction.atomic
    def delete(*, milestone, user=None, request=None):
        if not can_manage_milestone(user, milestone.project):
            raise PermissionDenied
        project = milestone.project
        old_data = {
            "project": str(project.pk),
            "name": milestone.name,
            "status": milestone.status,
        }
        log_deleted(
            user=user,
            instance=milestone,
            old_data=old_data,
            request=request,
            verb="deleted milestone",
        )
        milestone.delete()
        return project
