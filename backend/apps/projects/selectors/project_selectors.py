from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from apps.accounts.models import User

from ..models import Milestone, Project, ProjectMember


class ProjectSelector:
    @staticmethod
    def visible_to(user):
        queryset = Project.objects.select_related(
            "owner__user", "department", "team"
        ).prefetch_related("memberships__employee__user", "milestones")
        if not getattr(user, "is_authenticated", False):
            return Project.objects.none()
        if user.is_superuser or user.role in (
            User.Role.ADMIN,
            User.Role.HR_MANAGER,
            User.Role.DEPARTMENT_ADMIN,
            User.Role.PROJECT_MANAGER,
            User.Role.MANAGER,
        ):
            return queryset
        return queryset.filter(
            Q(owner__user=user) | Q(memberships__employee__user=user)
        ).distinct()

    @staticmethod
    def active():
        return Project.objects.select_related(
            "owner__user", "department", "team"
        ).filter(is_archived=False)

    @staticmethod
    def search_and_filter(queryset, *, search=None, status=None, priority=None):
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(code__icontains=search)
                | Q(description__icontains=search)
                | Q(department__name__icontains=search)
                | Q(team__name__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        return queryset

    @staticmethod
    def members_for(project):
        return ProjectMember.objects.select_related(
            "employee__user", "employee__department"
        ).filter(project=project)

    @staticmethod
    def milestones_for(project):
        return Milestone.objects.filter(project=project).order_by("due_date", "name")

    @staticmethod
    def dashboard_metrics(user=None):
        queryset = (
            ProjectSelector.visible_to(user) if user else ProjectSelector.active()
        )
        upcoming_cutoff = timezone.localdate() + timedelta(days=30)
        milestones = Milestone.objects.select_related("project").filter(
            project__in=queryset,
            status__in=[Milestone.Status.NOT_STARTED, Milestone.Status.IN_PROGRESS],
            due_date__lte=upcoming_cutoff,
        )
        return {
            "total_projects": queryset.count(),
            "active_projects": queryset.filter(status=Project.Status.ACTIVE).count(),
            "projects_by_status": queryset.values("status").annotate(total=Count("id")),
            "upcoming_milestones": milestones.order_by("due_date")[:8],
        }


class MilestoneSelector:
    @staticmethod
    def visible_to(user):
        return Milestone.objects.select_related(
            "project", "project__owner__user"
        ).filter(project__in=ProjectSelector.visible_to(user))

    @staticmethod
    def progress_for(project):
        total = project.milestones.count()
        completed = project.milestones.filter(status=Milestone.Status.COMPLETED).count()
        percentage = round((completed / total) * 100) if total else 0
        return {"total": total, "completed": completed, "percentage": percentage}
