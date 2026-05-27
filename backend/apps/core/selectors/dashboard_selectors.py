from apps.accounts.models import User
from apps.core.models import Activity, ApprovalInstance
from apps.employees.models import Department, EmployeeProfile
from apps.notifications.services.notification_service import NotificationService
from apps.projects.selectors.project_selectors import ProjectSelector


class DashboardSelector:
    @staticmethod
    def metrics_for(user):
        project_metrics = ProjectSelector.dashboard_metrics(user)
        return {
            "total_employees": EmployeeProfile.objects.count(),
            "active_employees": EmployeeProfile.objects.filter(
                employment_status=EmployeeProfile.EmploymentStatus.ACTIVE
            ).count(),
            "active_departments": Department.objects.filter(is_active=True).count(),
            "managers_count": User.objects.filter(
                role__in=[
                    User.Role.MANAGER,
                    User.Role.PROJECT_MANAGER,
                    User.Role.HR_MANAGER,
                    User.Role.DEPARTMENT_ADMIN,
                ],
                is_active=True,
            ).count(),
            "pending_approvals": ApprovalInstance.objects.filter(
                status=ApprovalInstance.Status.PENDING
            ).count(),
            "recent_activities": Activity.objects.select_related("actor").order_by(
                "-timestamp"
            )[:8],
            "unread_notifications": NotificationService.unread_count(user),
            **project_metrics,
        }
