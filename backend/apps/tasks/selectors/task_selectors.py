from django.db.models import Count, Q
from django.utils import timezone

from apps.accounts.models import User
from apps.projects.models import ProjectMember

from ..models import (
    Task,
    TaskActivity,
    TaskAssignment,
    TaskChecklist,
    TaskDependency,
)


class TaskSelector:
    @staticmethod
    def base_queryset():
        return Task.objects.select_related(
            "project",
            "milestone",
            "created_by__user",
            "updated_by__user",
        ).prefetch_related(
            "assignments__employee__user",
            "checklists__items",
            "attachments",
        )

    @staticmethod
    def visible_to(user):
        queryset = TaskSelector.base_queryset()
        if not getattr(user, "is_authenticated", False):
            return Task.objects.none()
        if user.is_superuser or user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.HR_MANAGER:
            # HR Manager should not have access to tasks
            return Task.objects.none()
        if user.role == User.Role.DEPARTMENT_ADMIN:
            # Department Admin can see tasks in their department's projects
            return queryset.filter(project__department__name=user.department)
        if user.role in (User.Role.PROJECT_MANAGER, User.Role.MANAGER):
            return queryset
        return queryset.filter(
            Q(created_by__user=user)
            | Q(assignments__employee__user=user)
            | Q(project__owner__user=user)
            | Q(project__memberships__employee__user=user)
        ).distinct()

    @staticmethod
    def active_for(user):
        return TaskSelector.visible_to(user).filter(is_archived=False)

    @staticmethod
    def filtered(
        queryset,
        *,
        search=None,
        status=None,
        priority=None,
        assignee=None,
        project=None,
        milestone=None,
        created_by=None,
        start_date=None,
        due_date=None,
    ):
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(task_code__icontains=search)
                | Q(project__name__icontains=search)
                | Q(project__code__icontains=search)
                | Q(milestone__name__icontains=search)
                | Q(assignments__employee__user__full_name__icontains=search)
            ).distinct()
        if status:
            queryset = queryset.filter(status=status)
        if priority:
            queryset = queryset.filter(priority=priority)
        if assignee:
            queryset = queryset.filter(assignments__employee_id=assignee)
        if project:
            queryset = queryset.filter(project_id=project)
        if milestone:
            queryset = queryset.filter(milestone_id=milestone)
        if created_by:
            queryset = queryset.filter(created_by_id=created_by)
        if start_date:
            queryset = queryset.filter(due_date__gte=start_date)
        if due_date:
            queryset = queryset.filter(due_date__lte=due_date)
        return queryset.distinct()

    @staticmethod
    def board_for(user, *, project=None, milestone=None):
        queryset = TaskSelector.active_for(user)
        if project:
            queryset = queryset.filter(project_id=project)
        if milestone:
            queryset = queryset.filter(milestone_id=milestone)
        return queryset.order_by("status", "priority", "due_date", "created_at")

    @staticmethod
    def detail_for(user, pk):
        return TaskSelector.visible_to(user).get(pk=pk)

    @staticmethod
    def assignments_for(task):
        return TaskAssignment.objects.select_related(
            "employee__user", "assigned_by__user"
        ).filter(task=task)

    @staticmethod
    def comments_for(task):
        return task.comments.select_related("author__user", "parent").prefetch_related(
            "replies"
        )

    @staticmethod
    def activities_for(task):
        return TaskActivity.objects.select_related("actor__user").filter(task=task)

    @staticmethod
    def checklists_for(task):
        return TaskChecklist.objects.prefetch_related(
            "items__completed_by__user"
        ).filter(task=task)

    @staticmethod
    def dependencies_for(task):
        return TaskDependency.objects.select_related(
            "predecessor_task", "successor_task"
        ).filter(successor_task=task)

    @staticmethod
    def assignee_options_for(user):
        employee_ids = ProjectMember.objects.filter(
            project__tasks__in=TaskSelector.visible_to(user)
        ).values_list("employee_id", flat=True)
        from apps.employees.models import EmployeeProfile

        return (
            EmployeeProfile.objects.select_related("user")
            .filter(id__in=employee_ids)
            .distinct()
        )


class TaskReportSelector:
    @staticmethod
    def status_counts(user):
        return (
            TaskSelector.active_for(user)
            .values("status")
            .annotate(total=Count("id"))
            .order_by("status")
        )

    @staticmethod
    def priority_counts(user):
        return (
            TaskSelector.active_for(user)
            .values("priority")
            .annotate(total=Count("id"))
            .order_by("priority")
        )

    @staticmethod
    def overdue(user):
        today = timezone.localdate()
        return TaskSelector.active_for(user).filter(
            due_date__lt=today,
            status__in=[
                Task.Status.BACKLOG,
                Task.Status.TODO,
                Task.Status.IN_PROGRESS,
                Task.Status.REVIEW,
                Task.Status.BLOCKED,
            ],
        )
