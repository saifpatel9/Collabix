from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class Phase9OnboardingTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(
            email="test.user@company.com",
            password="Test@1234",
            full_name="Test User",
            role="employee",
            department="IT",
            is_active=True,
        )

        self.user.must_change_password = True
        self.user.save()

    # -------------------------------------------------------
    # 1. LOGIN FLOW TEST (FORCED REDIRECT)
    # -------------------------------------------------------
    def test_login_redirects_to_change_password_when_required(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "test.user@company.com", "password": "Test@1234"},
            follow=True
        )

        self.user.refresh_from_db()

        # Should land on password change page
        redirect_urls = [url for url, status in response.redirect_chain]

        self.assertIn(
            reverse("accounts:change_password"),
            redirect_urls,
            )

    # -------------------------------------------------------
    # 2. MIDDLEWARE ENFORCEMENT TEST
    # -------------------------------------------------------
    def test_dashboard_blocked_when_password_change_required(self):
        self.user.must_change_password = True
        self.user.save()

        # Refresh object from DB
        self.user.refresh_from_db()

        # Login AFTER refresh
        self.client.force_login(self.user)

        response = self.client.get("/dashboard/", follow=False)

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            response.url,
            reverse("accounts:change_password"),
        )
    # -------------------------------------------------------
    # 3. PASSWORD CHANGE FLOW TEST
    # -------------------------------------------------------
    def test_password_change_resets_flag(self):
        self.client.login(email="test.user@company.com", password="Test@1234")

        response = self.client.post(
            reverse("accounts:change_password"),
            {
                "old_password": "Test@1234",
                "new_password1": "NewPass@1234",
                "new_password2": "NewPass@1234",
            },
            follow=True
        )

        self.user.refresh_from_db()

        self.assertFalse(self.user.must_change_password)
        self.assertContains(response, "successfully")

    # -------------------------------------------------------
    # 4. LOGIN AFTER PASSWORD CHANGE
    # -------------------------------------------------------
    def test_login_after_password_change_works_normally(self):
        self.user.must_change_password = False
        self.user.set_password("NewPass@1234")
        self.user.save()

        login = self.client.login(
            email="test.user@company.com",
            password="NewPass@1234"
        )

        self.assertTrue(login)

        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 200)

    # -------------------------------------------------------
    # 5. PASSWORD RESET FLOW TEST
    # -------------------------------------------------------
    def test_password_reset_flow(self):
        response = self.client.post(
            reverse("accounts:password_reset"),
            {"email": "test.user@company.com"},
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        # We cannot test email sending (no email backend),
        # but we ensure endpoint works
        self.assertContains(response, "Check your email", status_code=200)

    # -------------------------------------------------------
    # 6. MIDDLEWARE LOOP PROTECTION TEST
    # -------------------------------------------------------
    def test_no_redirect_loop_on_change_password_page(self):
        self.client.login(email="test.user@company.com", password="Test@1234")

        response = self.client.get(reverse("accounts:change_password"))

        # Should NOT loop redirect
        self.assertNotEqual(response.status_code, 500)
        self.assertIn(response.status_code, [200, 302])

    # -------------------------------------------------------
    # 7. STATE TRANSITION INTEGRITY
    # -------------------------------------------------------
    def test_must_change_password_state_integrity(self):
        self.assertTrue(self.user.must_change_password)

        self.client.login(email="test.user@company.com", password="Test@1234")

        self.client.post(
            reverse("accounts:change_password"),
            {
                "old_password": "Test@1234",
                "new_password1": "NewPass@1234",
                "new_password2": "NewPass@1234",
            }
        )

        self.user.refresh_from_db()
        self.assertFalse(self.user.must_change_password)