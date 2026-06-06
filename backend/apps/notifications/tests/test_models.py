from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.notifications.models import Notification, NotificationPreference

User = get_user_model()


class NotificationModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="TestPass123!",
            full_name="Test User"
        )

    def test_notification_creation(self):
        notification = Notification.objects.create(
            recipient=self.user,
            title="Test Notification",
            message="Test message",
            notification_type=Notification.Type.INFO,
            category=Notification.Type.SYSTEM
        )
        self.assertEqual(notification.recipient, self.user)
        self.assertEqual(notification.title, "Test Notification")
        self.assertEqual(notification.is_read, False)

    def test_notification_preference_creation(self):
        pref = NotificationPreference.objects.create(user=self.user)
        self.assertEqual(pref.user, self.user)
        self.assertTrue(pref.task_notifications)

    def test_notification_preference_allows(self):
        pref = NotificationPreference.objects.create(user=self.user)
        self.assertTrue(pref.allows(Notification.Category.TASK))
        self.assertTrue(pref.allows(Notification.Category.MENTION))
        pref.task_notifications = False
        pref.save()
        self.assertFalse(pref.allows(Notification.Category.TASK))

    def test_notification_ordering(self):
        n1 = Notification.objects.create(recipient=self.user, title="1", message="")
        n2 = Notification.objects.create(recipient=self.user, title="2", message="")
        notifications = Notification.objects.all()
        self.assertEqual(notifications[0], n2)
        self.assertEqual(notifications[1], n1)
