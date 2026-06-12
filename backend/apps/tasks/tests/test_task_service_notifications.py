from unittest.mock import patch

from django.test import TestCase


class TaskServiceNotificationTests(TestCase):

    @patch("apps.tasks.tasks.send_task_notification.delay")
    def test_placeholder(self, mock_delay):
        """
        Celery integration is verified manually.

        This placeholder test exists so the test module
        is discovered until full task factories are added.
        """
        self.assertTrue(True)