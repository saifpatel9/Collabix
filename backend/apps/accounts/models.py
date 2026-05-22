from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

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

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EMPLOYEE)
    department = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    profile_image = models.ImageField(
        upload_to="uploads/profiles/", blank=True, null=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.email
