from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from apps.notifications.models import Notification

User = get_user_model()


class NotificationHTMXTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            email="test@example.com",
            password="TestPass123!",
            full_name="Test User",
        )

        self.user.must_change_password = False
        self.user.save(update_fields=["must_change_password"])

        self.client.force_login(self.user)

    def test_htmx_partial_rendering(self):
        Notification.objects.create(recipient=self.user, title="Test", message="")
        response = self.client.get(
            reverse("notifications:center"),
            HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "notifications/partials/notification_list.html")

    def test_htmx_dropdown_update(self):
        n = Notification.objects.create(recipient=self.user, title="Test", message="", is_read=False)
        response = self.client.post(
            reverse("notifications:mark_read", kwargs={"pk": n.pk}),
            {"response_scope": "dropdown"},
            HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "components/notification_dropdown.html")

    def test_htmx_unread_count_sync(self):
        n = Notification.objects.create(recipient=self.user, title="Test", message="", is_read=False)
        response = self.client.post(
            reverse("notifications:mark_read", kwargs={"pk": n.pk}),
            {"response_scope": "center"},
            HTTP_HX_REQUEST="true"
        )
        self.assertContains(response, "hx-swap-oob")
