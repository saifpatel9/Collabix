from django.db.models import Count, Sum
from django.utils import timezone

from apps.accounts.models import User
from apps.core.models import ApprovalInstance
from apps.employees.models import Department, EmployeeProfile
from apps.attendance.selectors.attendance_selectors import AttendanceSelector
from apps.notifications.services.notification_service import NotificationService
from apps.projects.models import Project
from apps.tasks.models import Task


class DashboardSelector:
    @staticmethod
    def metrics_for(user):
        today = timezone.localdate()
        thirty_days_ago = today - timezone.timedelta(days=30)
        visible_tasks = Task.objects.filter(is_archived=False)
        if user and user.is_authenticated and not user.is_superuser:
            from apps.tasks.selectors.task_selectors import TaskSelector
            visible_tasks = TaskSelector.active_for(user)
        overdue = visible_tasks.filter(
            due_date__lt=today,
            status__in=[Task.Status.BACKLOG, Task.Status.TODO, Task.Status.IN_PROGRESS, Task.Status.REVIEW, Task.Status.BLOCKED],
        )
        not_cancelled = visible_tasks.exclude(status=Task.Status.CANCELLED)
        completed = visible_tasks.filter(status=Task.Status.COMPLETED)
        employees = EmployeeProfile.objects.select_related("user", "department")
        active_emps = employees.filter(employment_status=EmployeeProfile.EmploymentStatus.ACTIVE)
        projects = Project.objects.filter(is_archived=False)
        budget_info = projects.aggregate(
            total_budget=Sum("budget"),
            project_count=Count("id"),
        )
        return {
            "total_employees": employees.count(),
            "active_employees": active_emps.count(),
            "new_employees": employees.filter(joining_date__gte=thirty_days_ago).count(),
            "departments_count": Department.objects.filter(is_active=True).count(),
            "departments": Department.objects.filter(is_active=True).annotate(emp_count=Count("employees")).order_by("name"),
            "managers_count": User.objects.filter(
                role__in=[User.Role.MANAGER, User.Role.PROJECT_MANAGER, User.Role.HR_MANAGER, User.Role.DEPARTMENT_ADMIN],
                is_active=True,
            ).count(),
            "pending_approvals": ApprovalInstance.objects.filter(status=ApprovalInstance.Status.PENDING).count(),
            "unread_notifications": NotificationService.unread_count(user),
            "total_projects": projects.count(),
            "active_projects": projects.filter(status=Project.Status.ACTIVE).count(),
            "total_tasks": visible_tasks.count(),
            "pending_tasks": visible_tasks.filter(status__in=[Task.Status.BACKLOG, Task.Status.TODO]).count(),
            "in_progress_tasks": visible_tasks.filter(status__in=[Task.Status.IN_PROGRESS, Task.Status.REVIEW]).count(),
            "completed_tasks": completed.count(),
            "overdue_tasks_count": overdue.count(),
            "total_budget": budget_info["total_budget"] or 0,
            "avg_budget": round((budget_info["total_budget"] or 0) / max(budget_info["project_count"] or 1, 1)),
            "employees": employees.order_by("-created_at")[:5],
            "projects_by_status": projects.values("status").annotate(total=Count("id")).order_by("status"),
            "tasks_by_priority": visible_tasks.values("priority").annotate(total=Count("id")).order_by("priority"),
            "tasks_by_status": visible_tasks.values("status").annotate(total=Count("id")).order_by("status"),
            "employee_status_counts": employees.values("employment_status").annotate(total=Count("id")),
            "task_completion_rate": round((completed.count() / max(not_cancelled.count(), 1)) * 100),
            "pending_leaves": AttendanceSelector.pending_leave_count(),
            "today_attendance": AttendanceSelector.today_summary(),
        }
