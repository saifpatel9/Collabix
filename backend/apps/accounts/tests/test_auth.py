from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.accounts.forms import validate_password_strength


User = get_user_model()


class PasswordValidationTests(TestCase):
    def test_password_too_short(self):
        with self.assertRaises(ValidationError):
            validate_password_strength("Short1!")
    
    def test_password_no_uppercase(self):
        with self.assertRaises(ValidationError):
            validate_password_strength("password123!")
    
    def test_password_no_number(self):
        with self.assertRaises(ValidationError):
            validate_password_strength("Password!")
    
    def test_password_no_special_char(self):
        with self.assertRaises(ValidationError):
            validate_password_strength("Password123")
    
    def test_valid_password(self):
        try:
            validate_password_strength("ValidPass123!")
        except ValidationError:
            self.fail("Valid password raised ValidationError")
    
    def test_password_similar_to_email(self):
        with self.assertRaises(ValidationError):
            validate_password_strength("user@example.com", user_email="user@example.com")


class EmployeeOnboardingTests(TestCase):
    def test_user_has_must_change_password_default(self):
        user = User.objects.create_user(
            email="testuser@example.com",
            full_name="Test User",
            password="TempPass123!"
        )
        self.assertFalse(user.must_change_password)
    
    def test_login_page_exists(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
    
    def test_change_password_page_requires_login(self):
        response = self.client.get(reverse("accounts:change_password"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse('accounts:change_password')}")
