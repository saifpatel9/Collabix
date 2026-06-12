import logging

from celery import shared_task

from apps.employees.models import EmployeeProfile
from apps.tasks.models import Task
from apps.tasks.services._helpers import notify_task_assignees
from apps.tasks.services.task_service import TaskService

logger = logging.getLogger(__name__)


@shared_task
def send_due_soon_reminders():
    count = TaskService.notify_due_soon(days=1)
    logger.info("Sent %s due-soon reminders", count)
    return count


@shared_task
def send_overdue_reminders():
    count = TaskService.notify_overdue()
    logger.info("Sent %s overdue reminders", count)
    return count


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_task_notification(
    task_id,
    title,
    message,
    action_url=None,
    exclude_employee_id=None,
):
    task = Task.objects.filter(pk=task_id).first()

    if not task:
        logger.warning(
            "Task %s no longer exists",
            task_id,
        )
        return

    exclude_employee = None

    if exclude_employee_id:
        exclude_employee = EmployeeProfile.objects.filter(
            pk=exclude_employee_id,
        ).first()

    notify_task_assignees(
        task=task,
        title=title,
        message=message,
        action_url=action_url or "",
        exclude_employee=exclude_employee,
    )

    logger.info(
        "Task notification sent for task_id=%s",
        task_id,
    )