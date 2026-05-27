from django.db import transaction

from ..models import Team, TeamMembership
from ._events import log_created, log_deleted, log_updated, notify_employee


class TeamService:
    @staticmethod
    @transaction.atomic
    def create(*, cleaned_data, user=None, request=None):
        team = Team.objects.create(**cleaned_data)
        if team.team_lead:
            TeamMembership.objects.get_or_create(
                team=team,
                employee=team.team_lead,
                defaults={"role": TeamMembership.Role.TEAM_LEAD},
            )
        log_created(
            user=user,
            instance=team,
            data={"name": team.name},
            request=request,
            verb="created team",
        )
        return team

    @staticmethod
    @transaction.atomic
    def update(*, team, cleaned_data, user=None, request=None):
        old_data = {"name": team.name, "is_active": team.is_active}
        for field, value in cleaned_data.items():
            setattr(team, field, value)
        team.save()
        if team.team_lead:
            TeamMembership.objects.update_or_create(
                team=team,
                employee=team.team_lead,
                defaults={"role": TeamMembership.Role.TEAM_LEAD},
            )
        log_updated(
            user=user,
            instance=team,
            old_data=old_data,
            new_data={"name": team.name, "is_active": team.is_active},
            request=request,
            verb="updated team",
        )
        return team

    @staticmethod
    @transaction.atomic
    def archive(*, team, user=None, request=None):
        old_data = {"is_active": team.is_active}
        team.is_active = False
        team.save(update_fields=["is_active", "updated_at"])
        log_updated(
            user=user,
            instance=team,
            old_data=old_data,
            new_data={"is_active": False},
            request=request,
            verb="archived team",
        )
        return team


class TeamMembershipService:
    @staticmethod
    @transaction.atomic
    def add_member(*, team, cleaned_data, user=None, request=None):
        membership, created = TeamMembership.objects.update_or_create(
            team=team,
            employee=cleaned_data["employee"],
            defaults={"role": cleaned_data["role"]},
        )
        verb = "added team member" if created else "updated team member"
        log_created(
            user=user,
            instance=membership,
            data={"team": str(team.pk), "employee": str(membership.employee_id)},
            request=request,
            verb=verb,
        )
        notify_employee(
            employee=membership.employee,
            title="Team membership updated",
            message=f"You were added to {team.name} as {membership.get_role_display()}.",
        )
        return membership

    @staticmethod
    @transaction.atomic
    def remove_member(*, membership, user=None, request=None):
        old_data = {
            "team": str(membership.team_id),
            "employee": str(membership.employee_id),
            "role": membership.role,
        }
        team = membership.team
        log_deleted(
            user=user,
            instance=membership,
            old_data=old_data,
            request=request,
            verb="removed team member",
        )
        membership.delete()
        return team
