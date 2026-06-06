from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.notifications.models import Notification
from apps.notifications.services.notification_service import NotificationService

User = get_user_model()


class NotificationServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="TestPass123!",
            full_name="Test User"
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="TestPass123!",
            full_name="Other User"
        )

    def test_create_notification(self):
        notification = NotificationService.create_notification(
            recipient=self.user,
            title="Test",
            message="Test message"
        )
        self.assertIsNotNone(notification)
        self.assertEqual(notification.recipient, self.user)
        self.assertEqual(Notification.objects.count(), 1)

    def test_unread_count(self):
        Notification.objects.create(recipient=self.user, title="1", message="", is_read=False)
        Notification.objects.create(recipient=self.user, title="2", message="", is_read=True)
        self.assertEqual(NotificationService.unread_count(self.user), 1)

    def test_recent_for(self):
        for i in range(10):
            Notification.objects.create(recipient=self.user, title=str(i), message="")
        recent = NotificationService.recent_for(self.user)
        self.assertEqual(len(recent), 8)

    def test_for_user(self):
        n = Notification.objects.create(recipient=self.user, title="1", message="")
        for_user = NotificationService.for_user(self.user)
        self.assertIn(n, for_user)

    def test_search_and_filter(self):
        n1 = Notification.objects.create(recipient=self.user, title="Apple", message="", is_read=False)
        n2 = Notification.objects.create(recipient=self.user, title="Banana", message="", is_read=True)
        n3 = Notification.objects.create(recipient=self.user, title="Cherry", message="", is_read=False, category=Notification.Category.TASK)
        queryset = NotificationService.for_user(self.user)
        filtered = NotificationService.search_and_filter(queryset, status="unread")
        self.assertEqual(len(filtered), 2)
        filtered = NotificationService.search_and_filter(queryset, status="read")
        self.assertEqual(len(filtered), 1)
        filtered = NotificationService.search_and_filter(queryset, search="Apple")
        self.assertEqual(len(filtered), 1)
        filtered = NotificationService.search_and_filter(queryset, category=Notification.Category.TASK)
        self.assertEqual(len(filtered), 1)

    def test_mark_as_read(self):
        n = Notification.objects.create(recipient=self.user, title="1", message="", is_read=False)
        NotificationService.mark_as_read(notification=n, user=self.user)
        n.refresh_from_db()
        self.assertTrue(n.is_read)

    def test_mark_as_unread(self):
        n = Notification.objects.create(recipient=self.user, title="1", message="", is_read=True)
        NotificationService.mark_as_unread(notification=n, user=self.user)
        n.refresh_from_db()
        self.assertFalse(n.is_read)

    def test_mark_as_read_ownership(self):
        n = Notification.objects.create(recipient=self.user, title="1", message="", is_read=False)
        NotificationService.mark_as_read(notification=n, user=self.other_user)
        n.refresh_from_db()
        self.assertFalse(n.is_read)

    def test_mark_as_unread_ownership(self):
        n = Notification.objects.create(recipient=self.user, title="1", message="", is_read=True)
        NotificationService.mark_as_unread(notification=n, user=self.other_user)
        n.refresh_from_db()
        self.assertTrue(n.is_read)

    def test_mark_all_read(self):
        Notification.objects.create(recipient=self.user, title="1", message="", is_read=False)
        Notification.objects.create(recipient=self.user, title="2", message="", is_read=False)
        Notification.objects.create(recipient=self.user, title="3", message="", is_read=True)
        updated = NotificationService.mark_all_read(user=self.user)
        self.assertEqual(updated, 2)
        self.assertEqual(Notification.objects.filter(is_read=False).count(), 0)
