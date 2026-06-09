from django.urls import path

from .views import (
    EmployeeDeactivateView,
    EmployeeDetailUpdateView,
    EmployeeListCreateView,
    EmployeeStatusView,
)

app_name = "employees"

urlpatterns = [
    path("", EmployeeListCreateView.as_view(), name="employee_list_create"),
    path("<uuid:pk>/", EmployeeDetailUpdateView.as_view(), name="employee_detail_update"),
    path("<uuid:pk>/status/", EmployeeStatusView.as_view(), name="employee_status"),
    path("<uuid:pk>/deactivate/", EmployeeDeactivateView.as_view(), name="employee_deactivate"),
]
