from apps.accounts.models import User
from apps.core.rbac.utils import is_admin
from apps.core.models import Activity, ApprovalInstance
from apps.employees.models import Department, EmployeeProfile
from apps.notifications.services.notification_service import NotificationService
from apps.projects.selectors.project_selectors import ProjectSelector
from apps.tasks.selectors.dashboard_selectors import TaskDashboardSelector


class DashboardSelector:
    @staticmethod
    def metrics_for(user):
        project_metrics = ProjectSelector.dashboard_metrics(user)
        task_metrics = TaskDashboardSelector.metrics_for(user)
        user_is_admin = is_admin(user)

        context = {
            "show_admin_stats": user_is_admin,
            "unread_notifications": NotificationService.unread_count(user),
            **project_metrics,
            **task_metrics,
        }

        if user_is_admin:
            context.update(
                {
                    "total_employees": EmployeeProfile.objects.count(),
                    "active_employees": EmployeeProfile.objects.filter(
                        employment_status=EmployeeProfile.EmploymentStatus.ACTIVE
                    ).count(),
                    "active_departments": Department.objects.filter(is_active=True).count(),
                    "pending_approvals": ApprovalInstance.objects.filter(
                        status=ApprovalInstance.Status.PENDING
                    ).count(),
                }
            )

        if user_is_admin:
            recent_activities = Activity.objects.select_related("actor").order_by(
                "-timestamp"
            )[:8]
        else:
            recent_activities = Activity.objects.select_related("actor").filter(
                actor=user
            ).order_by("-timestamp")[:8]
        context["recent_activities"] = recent_activities

        return context
