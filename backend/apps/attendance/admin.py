from django.contrib import admin

from .models import Attendance, Holiday, LeaveRequest, LeaveType, Shift


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ["name", "start_time", "end_time", "grace_period_minutes", "is_active"]
    list_filter = ["is_active"]


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ["name", "date", "is_recurring"]
    list_filter = ["is_recurring", "date"]


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "days_allowed", "requires_approval", "is_active"]
    list_filter = ["is_active"]


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ["employee", "leave_type", "start_date", "end_date", "status", "created_at"]
    list_filter = ["status", "leave_type"]
    search_fields = ["employee__user__full_name", "reason"]


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ["employee", "date", "status", "check_in", "check_out", "worked_hours"]
    list_filter = ["status", "date"]
    search_fields = ["employee__user__full_name"]
