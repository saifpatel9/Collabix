from django.db.models import Count, Sum, Q
from django.utils import timezone

from apps.attendance.models import Attendance, Holiday, LeaveRequest, LeaveType, Shift


class AttendanceSelector:
    @staticmethod
    def for_employee(employee, start_date=None, end_date=None):
        qs = Attendance.objects.filter(employee=employee).select_related("shift")
        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)
        return qs.order_by("-date")

    @staticmethod
    def daily_report(date=None):
        date = date or timezone.localdate()
        return Attendance.objects.filter(date=date).select_related("employee__user", "shift")

    @staticmethod
    def monthly_summary(employee, year, month):
        start = timezone.date(year, month, 1)
        if month == 12:
            end = timezone.date(year + 1, 1, 1)
        else:
            end = timezone.date(year, month + 1, 1)
        records = Attendance.objects.filter(employee=employee, date__gte=start, date__lt=end)
        summary = records.aggregate(
            total_days=Count("id"),
            present=Count("id", filter=Q(status=Attendance.Status.PRESENT)),
            absent=Count("id", filter=Q(status=Attendance.Status.ABSENT)),
            late=Count("id", filter=Q(status=Attendance.Status.LATE)),
            half_day=Count("id", filter=Q(status=Attendance.Status.HALF_DAY)),
            on_leave=Count("id", filter=Q(status=Attendance.Status.ON_LEAVE)),
            total_worked=Sum("worked_hours"),
            total_overtime=Sum("overtime_hours"),
        )
        return summary

    @staticmethod
    def all_shifts(active_only=True):
        qs = Shift.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)
        return qs.order_by("start_time")

    @staticmethod
    def all_holidays(year=None):
        qs = Holiday.objects.all()
        if year:
            qs = qs.filter(date__year=year)
        return qs.order_by("date")

    @staticmethod
    def all_leave_types(active_only=True):
        qs = LeaveType.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)
        return qs

    @staticmethod
    def leave_requests_for(employee=None, status=None):
        qs = LeaveRequest.objects.select_related("employee__user", "leave_type", "approved_by__user")
        if employee:
            qs = qs.filter(employee=employee)
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-created_at")

    @staticmethod
    def pending_leave_count():
        return LeaveRequest.objects.filter(status=LeaveRequest.Status.PENDING).count()

    @staticmethod
    def today_summary():
        today = timezone.localdate()
        return Attendance.objects.filter(date=today).aggregate(
            total=Count("id"),
            present=Count("id", filter=Q(status=Attendance.Status.PRESENT)),
            absent=Count("id", filter=Q(status=Attendance.Status.ABSENT)),
            late=Count("id", filter=Q(status=Attendance.Status.LATE)),
            on_leave=Count("id", filter=Q(status=Attendance.Status.ON_LEAVE)),
        )
