import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from apps.core.models import TimeStampedUUIDModel

from .managers import UserManager


class User(TimeStampedUUIDModel, AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        DEPARTMENT_ADMIN = "department_admin", "Department Admin"
        HR_MANAGER = "hr_manager", "HR Manager"
        PROJECT_MANAGER = "project_manager", "Project Manager"
        MANAGER = "manager", "Manager"
        EMPLOYEE = "employee", "Employee"

    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    department = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(
        upload_to="uploads/profiles/", blank=True, null=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    must_change_password = models.BooleanField(default=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.email


class OTPCode(models.Model):
    class Purpose(models.TextChoices):
        PASSWORD_RESET = "password_reset", "Password Reset"
        EMAIL_VERIFICATION = "email_verification", "Email Verification"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="otp_codes"
    )
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=30, choices=Purpose.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = "auth_otp_codes"
        indexes = [
            models.Index(fields=["user", "purpose", "is_used"]),
        ]

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at

    def __str__(self) -> str:
        return f"{self.user.email} - {self.purpose}"


class EmployeeOnboardingToken(TimeStampedUUIDModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="onboarding_tokens")
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = "auth_employee_onboarding_tokens"
        ordering = ["-created_at"]

    def is_valid(self):
        return not self.is_used and timezone.now() <= self.expires_at

    def __str__(self):
        return f"{self.user.email} - {self.token}"


class LoginHistory(models.Model):
    class LoginMethod(models.TextChoices):
        PASSWORD = "password", "Password"
        OTP = "otp", "OTP"
        SESSION = "session", "Session"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="login_history"
    )
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    method = models.CharField(
        max_length=20, choices=LoginMethod.choices, default=LoginMethod.PASSWORD
    )
    success = models.BooleanField(default=True)
    failure_reason = models.CharField(max_length=255, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "-timestamp"]),
        ]
        
    def __str__(self) -> str:
        status = "success" if self.success else "failed"
        return f"{self.user.email} - {status} at {self.timestamp}"
