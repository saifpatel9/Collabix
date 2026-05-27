from django.db import transaction

from ..models import ProjectMember
from ._events import log_created, log_deleted, log_updated, notify_employee


class ProjectMemberService:
    @staticmethod
    @transaction.atomic
    def add_member(*, project, cleaned_data, user=None, request=None):
        member, created = ProjectMember.objects.update_or_create(
            project=project,
            employee=cleaned_data["employee"],
            defaults={"role": cleaned_data["role"]},
        )
        log_created(
            user=user,
            instance=member,
            data={"project": str(project.pk), "employee": str(member.employee_id)},
            request=request,
            verb="added project member" if created else "updated project member",
        )
        notify_employee(
            employee=member.employee,
            title="Project membership updated",
            message=f"You were added to {project.name} as {member.get_role_display()}.",
        )
        return member

    @staticmethod
    @transaction.atomic
    def change_role(*, member, role, user=None, request=None):
        old_data = {"role": member.role}
        member.role = role
        member.save(update_fields=["role", "updated_at"])
        log_updated(
            user=user,
            instance=member,
            old_data=old_data,
            new_data={"role": member.role},
            request=request,
            verb="changed project member role",
        )
        notify_employee(
            employee=member.employee,
            title="Project role changed",
            message=f"Your role on {member.project.name} is now {member.get_role_display()}.",
        )
        return member

    @staticmethod
    @transaction.atomic
    def remove_member(*, member, user=None, request=None):
        old_data = {
            "project": str(member.project_id),
            "employee": str(member.employee_id),
            "role": member.role,
        }
        project = member.project
        log_deleted(
            user=user,
            instance=member,
            old_data=old_data,
            request=request,
            verb="removed project member",
        )
        member.delete()
        return project
