from django.urls import path

from . import views

app_name = "attendance"

urlpatterns = [
    path("attendance/", views.AttendanceDashboardView.as_view(), name="dashboard"),
    path("attendance/all/", views.AttendanceListView.as_view(), name="list"),
    path("attendance/create/", views.AttendanceCreateView.as_view(), name="create"),
    path("attendance/<uuid:pk>/edit/", views.AttendanceUpdateView.as_view(), name="update"),
    path("attendance/my/", views.MyAttendanceView.as_view(), name="my_attendance"),
    path("shifts/", views.ShiftListView.as_view(), name="shift_list"),
    path("shifts/create/", views.ShiftCreateView.as_view(), name="shift_create"),
    path("shifts/<uuid:pk>/edit/", views.ShiftUpdateView.as_view(), name="shift_update"),
    path("leave-types/", views.LeaveTypeListView.as_view(), name="leavetype_list"),
    path("leave-types/create/", views.LeaveTypeCreateView.as_view(), name="leavetype_create"),
    path("leave-types/<uuid:pk>/edit/", views.LeaveTypeUpdateView.as_view(), name="leavetype_update"),
    path("leaves/", views.LeaveRequestListView.as_view(), name="leave_list"),
    path("leaves/apply/", views.LeaveRequestCreateView.as_view(), name="leave_apply"),
    path("leaves/<uuid:pk>/approve/", views.LeaveRequestApproveView.as_view(), name="leave_approve"),
    path("leaves/<uuid:pk>/reject/", views.LeaveRequestRejectView.as_view(), name="leave_reject"),
    path("holidays/", views.HolidayListView.as_view(), name="holiday_list"),
    path("holidays/create/", views.HolidayCreateView.as_view(), name="holiday_create"),
    path("holidays/<uuid:pk>/edit/", views.HolidayUpdateView.as_view(), name="holiday_update"),
]
