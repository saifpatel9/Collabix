from django import forms

from .models import Attendance, Holiday, LeaveRequest, LeaveType, Shift


class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ["name", "start_time", "end_time", "grace_period_minutes", "is_active"]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time", "class": "form-input"}),
            "end_time": forms.TimeInput(attrs={"type": "time", "class": "form-input"}),
        }


class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = ["name", "date", "is_recurring"]
        widgets = {"date": forms.DateInput(attrs={"type": "date", "class": "form-input"})}


class LeaveTypeForm(forms.ModelForm):
    class Meta:
        model = LeaveType
        fields = ["name", "code", "days_allowed", "requires_approval", "is_active"]


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ["leave_type", "start_date", "end_date", "reason"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            "reason": forms.Textarea(attrs={"rows": 3, "class": "form-input"}),
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["employee", "date", "shift", "check_in", "check_out", "status", "worked_hours", "overtime_hours", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            "check_in": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-input"}),
            "check_out": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-input"}),
            "notes": forms.Textarea(attrs={"rows": 2, "class": "form-input"}),
        }
