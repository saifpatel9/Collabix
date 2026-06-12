from unittest.mock import patch

from django.test import TestCase

from apps.tasks.tasks import send_task_notification


class SendTaskNotificationTests(TestCase):

    def test_missing_task_returns_without_error(self):
        send_task_notification(
            999999,
            "Test",
            "Test message",
        )

    @patch("apps.tasks.tasks.notify_task_assignees")
    @patch("apps.tasks.tasks.Task")
    def test_notification_sent_for_existing_task(
        self,
        mock_task_model,
        mock_notify,
    ):
        mock_task = object()

        mock_task_model.objects.filter.return_value.first.return_value = (
            mock_task
        )

        send_task_notification(
            1,
            "Task completed",
            "Completed",
        )

        mock_notify.assert_called_once()