import logging

from celery import shared_task

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