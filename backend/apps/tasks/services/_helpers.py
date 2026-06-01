from apps.core.services.audit_service import AuditService
from apps.notifications.models import Notification
from apps.notifications.services.notification_service import NotificationService


def request_ip(request):
    if not request:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def employee_for_user(user):
    if not getattr(user, "is_authenticated", False):
        return None
    return getattr(user, "employee_profile", None)


def audit_create(*, user, instance, data=None, request=None):
    return AuditService.log_create(
        user=user, instance=instance, new_data=data, ip_address=request_ip(request)
    )


def audit_update(*, user, instance, old_data=None, new_data=None, request=None):
    return AuditService.log_update(
        user=user,
        instance=instance,
        old_data=old_data,
        new_data=new_data,
        ip_address=request_ip(request),
    )


def audit_delete(*, user, instance, old_data=None, request=None):
    return AuditService.log_delete(
        user=user, instance=instance, old_data=old_data, ip_address=request_ip(request)
    )


def notify_employee(
    *,
    employee,
    title,
    message,
    notification_type=Notification.Type.INFO,
    category=Notification.Category.TASK,
    action_url="",
    target=None,
):
    if employee and employee.user_id:
        return NotificationService.create_notification(
            recipient=employee.user,
            title=title,
            message=message,
            notification_type=notification_type,
            category=category,
            action_url=action_url,
            target=target,
        )
    return None


def notify_task_assignees(
    *,
    task,
    title,
    message,
    exclude_employee=None,
    notification_type=Notification.Type.INFO,
    category=Notification.Category.TASK,
    action_url="",
):
    recipients = task.assignments.select_related("employee__user")
    if exclude_employee:
        recipients = recipients.exclude(employee=exclude_employee)
    for assignment in recipients:
        notify_employee(
            employee=assignment.employee,
            title=title,
            message=message,
            notification_type=notification_type,
            category=category,
            action_url=action_url,
            target=task,
        )
