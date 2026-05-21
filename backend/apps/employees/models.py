from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedUUIDModel


class EmployeeBaseModel(TimeStampedUUIDModel):
    class Meta:
        abstract = True


class Department(EmployeeBaseModel):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    head = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="headed_departments",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "departments"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"], name="dept_name_idx"),
            models.Index(fields=["is_active"], name="dept_active_idx"),
        ]

    def __str__(self) -> str:
        return self.name


class EmployeeProfile(EmployeeBaseModel):
    class EmploymentStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        ON_LEAVE = "on_leave", "On Leave"
        INACTIVE = "inactive", "Inactive"
        TERMINATED = "terminated", "Terminated"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
    )
    employee_id = models.CharField(max_length=50, unique=True)
    designation = models.CharField(max_length=150)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="employees",
    )
    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="direct_reports",
    )
    joining_date = models.DateField(blank=True, null=True)
    employment_status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE,
    )
    bio = models.TextField(blank=True)

    class Meta:
        db_table = "employee_profiles"
        ordering = ["user__full_name"]
        indexes = [
            models.Index(fields=["employee_id"], name="emp_profile_emp_id_idx"),
            models.Index(fields=["employment_status"], name="emp_profile_status_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user.full_name} ({self.employee_id})"
