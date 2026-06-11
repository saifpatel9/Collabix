from unittest.mock import patch

from apps.tasks.tasks import (
    send_due_soon_reminders,
    send_overdue_reminders,
)


class TestCeleryTasks:
    @patch("apps.tasks.tasks.TaskService.notify_due_soon")
    def test_send_due_soon_reminders(self, mock_notify):
        mock_notify.return_value = 3

        result = send_due_soon_reminders()

        mock_notify.assert_called_once_with(days=1)
        assert result == 3

    @patch("apps.tasks.tasks.TaskService.notify_overdue")
    def test_send_overdue_reminders(self, mock_notify):
        mock_notify.return_value = 5

        result = send_overdue_reminders()

        mock_notify.assert_called_once_with()
        assert result == 5