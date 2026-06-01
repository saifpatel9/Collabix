from django.utils import timezone

from ..models import Task, TaskActivity
from .task_selectors import TaskReportSelector, TaskSelector


class TaskDashboardSelector:
    @staticmethod
    def metrics_for(user):
        today = timezone.localdate()
        active = TaskSelector.active_for(user)
        my_tasks = active.filter(assignments__employee__user=user).distinct()
        due_today = active.filter(due_date=today).exclude(
            status__in=[Task.Status.COMPLETED, Task.Status.CANCELLED]
        )
        overdue = TaskReportSelector.overdue(user)
        return {
            "my_tasks": my_tasks[:8],
            "my_tasks_count": my_tasks.count(),
            "overdue_tasks": overdue[:8],
            "overdue_tasks_count": overdue.count(),
            "tasks_due_today": due_today[:8],
            "tasks_due_today_count": due_today.count(),
            "completed_tasks_count": active.filter(
                status=Task.Status.COMPLETED
            ).count(),
            "blocked_tasks_count": active.filter(status=Task.Status.BLOCKED).count(),
            "tasks_by_priority": TaskReportSelector.priority_counts(user),
            "tasks_by_status": TaskReportSelector.status_counts(user),
            "recent_task_activity": TaskActivity.objects.select_related(
                "task", "actor__user"
            ).filter(task__in=active)[:8],
        }
