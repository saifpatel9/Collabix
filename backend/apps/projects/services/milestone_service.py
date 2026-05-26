from django.db import transaction

from apps.core.services.audit_service import AuditService

from ..models import Milestone
from ._events import log_created, log_deleted, log_updated, request_ip


class MilestoneService:
    @staticmethod
    @transaction.atomic
    def create(*, project, cleaned_data, user=None, request=None):
        milestone = Milestone.objects.create(project=project, **cleaned_data)
        log_created(
            user=user,
            instance=milestone,
            data={"project": str(project.pk), "name": milestone.name},
            request=request,
            verb="created milestone",
        )
        return milestone

    @staticmethod
    @transaction.atomic
    def update(*, milestone, cleaned_data, user=None, request=None):
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
        return milestone

    @staticmethod
    @transaction.atomic
    def delete(*, milestone, user=None, request=None):
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
