from django.db import models, transaction
from django.utils import timezone

from apps.attendance.models import Attendance, Holiday, LeaveRequest, Shift
from apps.employees.models import EmployeeProfile


class AttendanceService:
    @staticmethod
    def check_in(employee, shift=None, notes=""):
        today = timezone.localdate()
        now = timezone.localtime()
        existing = Attendance.objects.filter(employee=employee, date=today).first()
        if existing:
            if existing.check_in:
                raise ValueError("Already checked in today.")
            existing.check_in = now
            existing.save()
            return existing
        status = Attendance.Status.PRESENT
        if shift and shift.start_time:
            scheduled = timezone.make_aware(
                timezone.datetime.combine(today, shift.start_time)
            )
            if now > scheduled + timezone.timedelta(minutes=shift.grace_period_minutes):
                status = Attendance.Status.LATE
        return Attendance.objects.create(
            employee=employee,
            date=today,
            shift=shift,
            check_in=now,
            status=status,
            notes=notes,
        )

    @staticmethod
    def check_out(employee):
        today = timezone.localdate()
        record = Attendance.objects.filter(employee=employee, date=today).first()
        if not record or record.check_out:
            raise ValueError("No active check-in session.")
        now = timezone.localtime()
        record.check_out = now
        if record.check_in:
            delta = now - record.check_in
            hours = delta.total_seconds() / 3600
            record.worked_hours = round(hours, 2)
            if record.shift:
                scheduled_hours = (
                    timezone.datetime.combine(today, record.shift.end_time)
                    - timezone.datetime.combine(today, record.shift.start_time)
                ).total_seconds() / 3600
                if hours > scheduled_hours:
                    record.overtime_hours = round(hours - scheduled_hours, 2)
        record.save()
        return record

    @staticmethod
    def mark_absent(employee, date, notes=""):
        return Attendance.objects.update_or_create(
            employee=employee,
            date=date,
            defaults={"status": Attendance.Status.ABSENT, "notes": notes},
        )[0]

    @staticmethod
    def auto_mark_absent():
        today = timezone.localdate()
        active_employees = EmployeeProfile.objects.filter(
            employment_status=EmployeeProfile.EmploymentStatus.ACTIVE
        )
        holidays = Holiday.objects.filter(date=today, is_recurring=False) | Holiday.objects.filter(
            date__month=today.month, date__day=today.day, is_recurring=True
        )
        holiday_dates = set(h.date for h in holidays)
        if today in holiday_dates:
            return []
        marked = []
        for emp in active_employees:
            _, created = Attendance.objects.get_or_create(
                employee=emp,
                date=today,
                defaults={"status": Attendance.Status.ABSENT},
            )
            if created:
                marked.append(_)
        return marked


class LeaveService:
    @staticmethod
    def apply(employee, leave_type, start_date, end_date, reason):
        return LeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
        )

    @staticmethod
    def approve(leave_request, approved_by):
        leave_request.status = LeaveRequest.Status.APPROVED
        leave_request.approved_by = approved_by
        leave_request.save()
        current = leave_request.start_date
        while current <= leave_request.end_date:
            Attendance.objects.update_or_create(
                employee=leave_request.employee,
                date=current,
                defaults={"status": Attendance.Status.ON_LEAVE},
            )
            current += timezone.timedelta(days=1)

    @staticmethod
    def reject(leave_request, approved_by):
        leave_request.status = LeaveRequest.Status.REJECTED
        leave_request.approved_by = approved_by
        leave_request.save()

    @staticmethod
    def cancel(leave_request):
        leave_request.status = LeaveRequest.Status.CANCELLED
        leave_request.save()
        Attendance.objects.filter(
            employee=leave_request.employee,
            date__range=[leave_request.start_date, leave_request.end_date],
        ).delete()

    @staticmethod
    def remaining_days(employee, leave_type):
        used = LeaveRequest.objects.filter(
            employee=employee,
            leave_type=leave_type,
            status=LeaveRequest.Status.APPROVED,
        ).aggregate(total=models.Sum(models.F("end_date") - models.F("start_date") + 1))
        used_days = used.get("total") or 0
        return max(leave_type.days_allowed - used_days, 0)
