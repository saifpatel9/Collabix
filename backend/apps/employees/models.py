from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import BaseModel


class EmployeeBaseModel(BaseModel):
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


class EmployeeHierarchy(EmployeeBaseModel):
    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name="hierarchy_assignments",
    )
    reporting_manager = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name="managed_hierarchy_assignments",
    )
    effective_from = models.DateField()
    effective_to = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "employee_hierarchies"
        ordering = ["-effective_from"]
        indexes = [
            models.Index(
                fields=["employee", "is_active"], name="emp_hierarchy_active_idx"
            ),
            models.Index(fields=["reporting_manager"], name="emp_hierarchy_mgr_idx"),
        ]

    def clean(self):
        if self.employee_id and self.employee_id == self.reporting_manager_id:
            raise ValidationError("Employee cannot report to self.")
        if self.effective_to and self.effective_from > self.effective_to:
            raise ValidationError(
                "Effective from date cannot be after effective to date."
            )
        if self.employee_id and self.is_active:
            duplicate = EmployeeHierarchy.objects.filter(
                employee_id=self.employee_id,
                is_active=True,
            )
            if self.pk:
                duplicate = duplicate.exclude(pk=self.pk)
            if duplicate.exists():
                raise ValidationError(
                    "Employee already has an active reporting manager."
                )

    def __str__(self) -> str:
        return f"{self.employee} -> {self.reporting_manager}"


class Designation(EmployeeBaseModel):
    title = models.CharField(max_length=150, unique=True)
    level = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    class Meta:
        db_table = "designations"
        ordering = ["level", "title"]
        indexes = [models.Index(fields=["level"], name="designation_level_idx")]

    def __str__(self) -> str:
        return self.title


class OrganizationPosition(EmployeeBaseModel):
    employee = models.OneToOneField(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name="organization_position",
    )
    designation = models.ForeignKey(
        Designation,
        on_delete=models.PROTECT,
        related_name="positions",
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="positions",
    )
    reporting_position = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="child_positions",
    )

    class Meta:
        db_table = "organization_positions"
        ordering = [
            "department__name",
            "designation__level",
            "employee__user__full_name",
        ]
        indexes = [
            models.Index(fields=["department"], name="org_position_dept_idx"),
            models.Index(fields=["designation"], name="org_position_desig_idx"),
        ]

    def clean(self):
        if self.reporting_position_id and self.reporting_position_id == self.id:
            raise ValidationError("A position cannot report to itself.")

    def __str__(self) -> str:
        return f"{self.employee.user.full_name} - {self.designation.title}"
