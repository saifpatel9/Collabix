from apps.core.services.activity_service import ActivityService
from apps.core.services.audit_service import AuditService
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


def notify_employee(*, employee, title, message):
    recipient = getattr(employee, "user", None)
    if recipient:
        NotificationService.create_notification(
            recipient=recipient, title=title, message=message
        )
