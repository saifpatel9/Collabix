from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel
from apps.employees.models import EmployeeProfile


class AttendanceBaseModel(BaseModel):
    class Meta:
        abstract = True


class Shift(AttendanceBaseModel):
    name = models.CharField(max_length=100, unique=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    grace_period_minutes = models.PositiveIntegerField(default=15)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "shifts"
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.name} ({self.start_time:%H:%M} - {self.end_time:%H:%M})"


class Holiday(AttendanceBaseModel):
    name = models.CharField(max_length=200)
    date = models.DateField()
    is_recurring = models.BooleanField(default=False)

    class Meta:
        db_table = "holidays"
        ordering = ["date"]
        constraints = [
            models.UniqueConstraint(fields=["name", "date"], name="uniq_holiday_name_date")
        ]

    def __str__(self):
        return f"{self.name} - {self.date}"


class LeaveType(AttendanceBaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    days_allowed = models.PositiveIntegerField()
    requires_approval = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "leave_types"
        ordering = ["name"]

    def __str__(self):
        return self.name


class LeaveRequest(AttendanceBaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name="leave_requests",
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.PROTECT,
        related_name="requests",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    approved_by = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="approved_leaves",
    )

    class Meta:
        db_table = "leave_requests"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["employee", "status"], name="leave_emp_status_idx"),
            models.Index(fields=["start_date", "end_date"], name="leave_date_range_idx"),
        ]

    @property
    def total_days(self):
        return (self.end_date - self.start_date).days + 1

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date cannot be after end date.")
        if self.start_date and self.start_date < timezone.localdate():
            raise ValidationError("Cannot apply for leave in the past.")

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.get_status_display()})"


class Attendance(AttendanceBaseModel):
    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"
        LATE = "late", "Late"
        HALF_DAY = "half_day", "Half Day"
        ON_LEAVE = "on_leave", "On Leave"

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name="attendances",
    )
    date = models.DateField()
    shift = models.ForeignKey(
        Shift,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="attendances",
    )
    check_in = models.DateTimeField(blank=True, null=True)
    check_out = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PRESENT,
    )
    worked_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "attendances"
        ordering = ["-date", "employee"]
        constraints = [
            models.UniqueConstraint(fields=["employee", "date"], name="uniq_employee_date")
        ]
        indexes = [
            models.Index(fields=["date"], name="attendance_date_idx"),
            models.Index(fields=["employee", "date"], name="attendance_emp_date_idx"),
            models.Index(fields=["status"], name="attendance_status_idx"),
        ]

    def clean(self):
        if self.check_in and self.check_out and self.check_in > self.check_out:
            raise ValidationError("Check-in cannot be after check-out.")

    def __str__(self):
        return f"{self.employee} - {self.date} ({self.get_status_display()})"
