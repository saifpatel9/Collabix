from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView, View

from apps.attendance.forms import AttendanceForm, HolidayForm, LeaveRequestForm, LeaveTypeForm, ShiftForm
from apps.attendance.models import Attendance, Holiday, LeaveRequest, LeaveType, Shift
from apps.attendance.selectors.attendance_selectors import AttendanceSelector
from apps.attendance.services.attendance_service import AttendanceService, LeaveService
from apps.core.mixins import PageSizeMixin
from apps.employees.models import EmployeeProfile


class AttendanceDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "attendance/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.localdate()
        selector = AttendanceSelector()
        employee = EmployeeProfile.objects.filter(user=self.request.user).first()
        ctx["today_summary"] = selector.today_summary()
        ctx["pending_leaves"] = selector.pending_leave_count()
        ctx["upcoming_holidays"] = selector.all_holidays()[:5]
        ctx["active_shifts"] = selector.all_shifts()
        if employee:
            ctx["my_attendance"] = selector.for_employee(employee, timezone.localdate() - timezone.timedelta(days=30))
            ctx["my_leaves"] = selector.leave_requests_for(employee=employee)[:5]
        return ctx


class AttendanceListView(LoginRequiredMixin, PageSizeMixin, ListView):
    model = Attendance
    template_name = "attendance/list.html"
    context_object_name = "attendances"

    def get_queryset(self):
        return AttendanceSelector().daily_report().select_related("employee__user", "shift")


class AttendanceCreateView(LoginRequiredMixin, CreateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = "attendance/form.html"
    success_url = reverse_lazy("attendance:list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Record Attendance"
        return ctx


class AttendanceUpdateView(LoginRequiredMixin, UpdateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = "attendance/form.html"
    success_url = reverse_lazy("attendance:list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = "Edit Attendance"
        return ctx


class ShiftListView(LoginRequiredMixin, ListView):
    model = Shift
    template_name = "attendance/shift_list.html"
    context_object_name = "shifts"


class ShiftCreateView(LoginRequiredMixin, CreateView):
    model = Shift
    form_class = ShiftForm
    template_name = "attendance/shift_form.html"
    success_url = reverse_lazy("attendance:shift_list")


class ShiftUpdateView(LoginRequiredMixin, UpdateView):
    model = Shift
    form_class = ShiftForm
    template_name = "attendance/shift_form.html"
    success_url = reverse_lazy("attendance:shift_list")


class LeaveTypeListView(LoginRequiredMixin, ListView):
    model = LeaveType
    template_name = "attendance/leavetype_list.html"
    context_object_name = "leave_types"


class LeaveTypeCreateView(LoginRequiredMixin, CreateView):
    model = LeaveType
    form_class = LeaveTypeForm
    template_name = "attendance/leavetype_form.html"
    success_url = reverse_lazy("attendance:leavetype_list")


class LeaveTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = LeaveType
    form_class = LeaveTypeForm
    template_name = "attendance/leavetype_form.html"
    success_url = reverse_lazy("attendance:leavetype_list")


class LeaveRequestListView(LoginRequiredMixin, PageSizeMixin, ListView):
    model = LeaveRequest
    template_name = "attendance/leaverequest_list.html"
    context_object_name = "leave_requests"

    def get_queryset(self):
        user = self.request.user
        employee = EmployeeProfile.objects.filter(user=user).first()
        return AttendanceSelector().leave_requests_for(employee=employee)


class LeaveRequestCreateView(LoginRequiredMixin, CreateView):
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = "attendance/leaverequest_form.html"
    success_url = reverse_lazy("attendance:leave_list")

    def form_valid(self, form):
        employee = EmployeeProfile.objects.get(user=self.request.user)
        form.instance.employee = employee
        return super().form_valid(form)


class LeaveRequestApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        leave = get_object_or_404(LeaveRequest, pk=pk)
        approver = EmployeeProfile.objects.get(user=request.user)
        LeaveService.approve(leave, approver)
        return redirect("attendance:leave_list")


class LeaveRequestRejectView(LoginRequiredMixin, View):
    def post(self, request, pk):
        leave = get_object_or_404(LeaveRequest, pk=pk)
        approver = EmployeeProfile.objects.get(user=request.user)
        LeaveService.reject(leave, approver)
        return redirect("attendance:leave_list")


class HolidayListView(LoginRequiredMixin, ListView):
    model = Holiday
    template_name = "attendance/holiday_list.html"
    context_object_name = "holidays"

    def get_queryset(self):
        return AttendanceSelector().all_holidays(year=timezone.localdate().year)


class HolidayCreateView(LoginRequiredMixin, CreateView):
    model = Holiday
    form_class = HolidayForm
    template_name = "attendance/holiday_form.html"
    success_url = reverse_lazy("attendance:holiday_list")


class HolidayUpdateView(LoginRequiredMixin, UpdateView):
    model = Holiday
    form_class = HolidayForm
    template_name = "attendance/holiday_form.html"
    success_url = reverse_lazy("attendance:holiday_list")


class MyAttendanceView(LoginRequiredMixin, TemplateView):
    template_name = "attendance/my_attendance.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        employee = EmployeeProfile.objects.filter(user=self.request.user).first()
        if employee:
            today = timezone.localdate()
            selector = AttendanceSelector()
            ctx["employee"] = employee
            ctx["attendance_records"] = selector.for_employee(employee, today.replace(month=1, day=1))
            ctx["monthly_summary"] = selector.monthly_summary(employee, today.year, today.month)
            ctx["leave_balance"] = LeaveType.objects.filter(is_active=True).values("id", "name", "days_allowed")
        return ctx
