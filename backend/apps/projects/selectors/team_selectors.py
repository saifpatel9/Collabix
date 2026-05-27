from django.db.models import Q

from apps.accounts.models import User

from ..models import Team, TeamMembership


class TeamSelector:
    @staticmethod
    def visible_to(user):
        queryset = Team.objects.select_related(
            "team_lead__user", "department"
        ).prefetch_related("memberships__employee__user")
        if not getattr(user, "is_authenticated", False):
            return Team.objects.none()
        if user.is_superuser or user.role in (
            User.Role.ADMIN,
            User.Role.HR_MANAGER,
            User.Role.DEPARTMENT_ADMIN,
            User.Role.PROJECT_MANAGER,
            User.Role.MANAGER,
        ):
            return queryset
        return queryset.filter(memberships__employee__user=user).distinct()

    @staticmethod
    def active():
        return Team.objects.select_related("team_lead__user", "department").filter(
            is_active=True
        )

    @staticmethod
    def search(queryset, search_term):
        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term)
                | Q(description__icontains=search_term)
                | Q(department__name__icontains=search_term)
                | Q(team_lead__user__full_name__icontains=search_term)
            )
        return queryset

    @staticmethod
    def memberships_for(team):
        return TeamMembership.objects.select_related(
            "employee__user", "employee__department"
        ).filter(team=team)
