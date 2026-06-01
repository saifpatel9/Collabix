from django.core.management.base import BaseCommand

from apps.tasks.services.task_service import TaskService


class Command(BaseCommand):
    help = "Send task due-soon and overdue notifications."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=1)

    def handle(self, *args, **options):
        due_soon_count = TaskService.notify_due_soon(days=options["days"])
        overdue_count = TaskService.notify_overdue()
        self.stdout.write(
            self.style.SUCCESS(
                f"Sent deadline notifications for {due_soon_count} due-soon "
                f"and {overdue_count} overdue tasks."
            )
        )
