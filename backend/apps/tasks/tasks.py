import logging

from celery import shared_task

from apps.employees.models import EmployeeProfile
from apps.tasks.models import Task
from apps.tasks.services._helpers import notify_task_assignees
from apps.tasks.services.task_service import TaskService

logger = logging.getLogger(__name__)


@shared_task
def send_due_soon_reminders():
    logger.info("Starting due-soon reminder task")

    count = TaskService.notify_due_soon(days=1)

    logger.info(
        "Due-soon reminder task completed reminders_sent=%s",
        count,
    )

    return count


@shared_task
def send_overdue_reminders():
    logger.info("Starting overdue reminder task")

    count = TaskService.notify_overdue()

    logger.info(
        "Overdue reminder task completed reminders_sent=%s",
        count,
    )

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
    logger.info(
        "Starting task notification task task_id=%s",
        task_id,
    )

    task = Task.objects.filter(pk=task_id).first()

    if not task:
        logger.warning(
            "Task notification aborted task_id=%s reason=task_not_found",
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
        "Task notification completed task_id=%s",
        task_id,
    )