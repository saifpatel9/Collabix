import logging

from celery import shared_task

from apps.employees.models import EmployeeProfile
from apps.notifications.models import Notification
from apps.notifications.services.notification_service import (
    NotificationService,
)

logger = logging.getLogger(__name__)


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def employee_onboarding(employee_id):
    logger.info(
        "Starting employee onboarding employee_id=%s",
        employee_id,
    )

    employee = (
        EmployeeProfile.objects.select_related(
            "user",
            "manager__user",
        )
        .filter(pk=employee_id)
        .first()
    )

    if not employee:
        logger.warning(
            "Employee onboarding aborted employee_id=%s reason=employee_not_found",
            employee_id,
        )
        return

    NotificationService.create_notification(
        recipient=employee.user,
        title="Welcome to Collabix",
        message=(
            f"Welcome aboard, {employee.user.full_name}. "
            "Your employee account has been created successfully."
        ),
        notification_type=Notification.Type.SUCCESS,
        category=Notification.Category.SYSTEM,
    )

    if employee.manager and employee.manager.user:
        NotificationService.create_notification(
            recipient=employee.manager.user,
            title="New Team Member",
            message=(
                f"{employee.user.full_name} has joined "
                "your reporting structure."
            ),
            notification_type=Notification.Type.INFO,
            category=Notification.Category.SYSTEM,
        )

    logger.info(
        "Employee onboarding completed employee_id=%s",
        employee_id,
    )