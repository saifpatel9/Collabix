from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.notifications.models import Notification

User = get_user_model()


class NotificationViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="TestPass123!",
            full_name="Test User"
        )
        self.client.force_login(self.user)

    def test_notification_center_loads(self):
        response = self.client.get(reverse("notifications:center"))
        self.assertEqual(response.status_code, 200)

    def test_mark_read_htmx(self):
        n = Notification.objects.create(recipient=self.user, title="1", message="", is_read=False)
        response = self.client.post(
            reverse("notifications:mark_read", kwargs={"pk": n.pk}),
            {"response_scope": "center"},
            HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        n.refresh_from_db()
        self.assertTrue(n.is_read)

    def test_mark_unread_htmx(self):
        n = Notification.objects.create(recipient=self.user, title="1", message="", is_read=True)
        response = self.client.post(
            reverse("notifications:mark_unread", kwargs={"pk": n.pk}),
            {"response_scope": "center"},
            HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        n.refresh_from_db()
        self.assertFalse(n.is_read)

    def test_mark_all_read_htmx(self):
        Notification.objects.create(recipient=self.user, title="1", message="", is_read=False)
        Notification.objects.create(recipient=self.user, title="2", message="", is_read=False)
        response = self.client.post(
            reverse("notifications:mark_all_read"),
            {"response_scope": "center"},
            HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Notification.objects.filter(is_read=False).count(), 0)

    def test_pagination(self):
        for i in range(25):
            Notification.objects.create(recipient=self.user, title=str(i), message="")
        response = self.client.get(reverse("notifications:center"), {"page": 2})
        self.assertEqual(response.status_code, 200)

    def test_search_filter(self):
        Notification.objects.create(recipient=self.user, title="Apple", message="")
        Notification.objects.create(recipient=self.user, title="Banana", message="")
        response = self.client.get(reverse("notifications:center"), {"q": "Apple"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Apple")

    def test_status_filter_unread(self):
        Notification.objects.create(recipient=self.user, title="Unread", message="", is_read=False)
        Notification.objects.create(recipient=self.user, title="Read", message="", is_read=True)
        response = self.client.get(reverse("notifications:center"), {"status": "unread"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unread")

    def test_status_filter_read(self):
        Notification.objects.create(recipient=self.user, title="Unread", message="", is_read=False)
        Notification.objects.create(recipient=self.user, title="Read", message="", is_read=True)
        response = self.client.get(reverse("notifications:center"), {"status": "read"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Read")

    def test_category_filter(self):
        Notification.objects.create(
            recipient=self.user, title="Task", message="",
            category=Notification.Category.TASK
        )
        response = self.client.get(
            reverse("notifications:center"),
            {"category": Notification.Category.TASK}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Task")
