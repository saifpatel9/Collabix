from apps.core.services.activity_service import ActivityService
from apps.core.services.audit_service import AuditService
from apps.notifications.models import Notification
from apps.notifications.services.notification_service import NotificationService


def request_ip(request):
    if not request:
        return None
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def log_created(*, user, instance, data=None, request=None, verb=None):
    AuditService.log_create(
        user=user, instance=instance, new_data=data, ip_address=request_ip(request)
    )
    if verb:
        ActivityService.record(actor=user, verb=verb, target=instance)


def log_updated(
    *, user, instance, old_data=None, new_data=None, request=None, verb=None
):
    AuditService.log_update(
        user=user,
        instance=instance,
        old_data=old_data,
        new_data=new_data,
        ip_address=request_ip(request),
    )
    if verb:
        ActivityService.record(actor=user, verb=verb, target=instance)


def log_deleted(*, user, instance, old_data=None, request=None, verb=None):
    AuditService.log_delete(
        user=user, instance=instance, old_data=old_data, ip_address=request_ip(request)
    )
    if verb:
        ActivityService.record(actor=user, verb=verb, target=instance)


def notify_employee(
    *,
    employee,
    title,
    message,
    notification_type=Notification.Type.INFO,
    category=Notification.Category.PROJECT,
    action_url="",
    target=None,
):
    recipient = getattr(employee, "user", None)
    if recipient:
        NotificationService.create_notification(
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
            category=category,
            action_url=action_url,
            target=target,
        )


def notify_project_members(
    *,
    project,
    title,
    message,
    notification_type=Notification.Type.INFO,
    action_url="",
    exclude_user=None,
    target=None,
):
    recipient_ids = set()
    if project.owner and project.owner.user_id:
        recipient_ids.add(project.owner.user_id)
    for membership in project.memberships.select_related("employee__user"):
        if membership.employee.user_id:
            recipient_ids.add(membership.employee.user_id)
    if exclude_user and getattr(exclude_user, "id", None) in recipient_ids:
        recipient_ids.remove(exclude_user.id)
    for user_id in recipient_ids:
        NotificationService.create_notification(
            recipient_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            category=Notification.Category.PROJECT,
            action_url=action_url,
            target=target or project,
        )
