from django.urls import path

from .views import (
    DepartmentCreateView,
    DepartmentDeleteView,
    DepartmentDetailView,
    DepartmentListView,
    DepartmentUpdateView,
    AssignManagerView,
    ChangeManagerView,
    EmployeeDirectoryView,
    EmployeeCreateView,
    EmployeeDetailView,
    OrganizationChartView,
    ReportingTreeView,
    EmployeeListView,
    EmployeeProfileView,
    EmployeeStatusUpdateView,
    EmployeeUpdateView,
)

app_name = "employees"

urlpatterns = [
    path("departments/", DepartmentListView.as_view(), name="department_list"),
    path(
        "departments/create/", DepartmentCreateView.as_view(), name="department_create"
    ),
    path(
        "departments/<uuid:pk>/",
        DepartmentDetailView.as_view(),
        name="department_detail",
    ),
    path(
        "departments/<uuid:pk>/edit/",
        DepartmentUpdateView.as_view(),
        name="department_update",
    ),
    path(
        "departments/<uuid:pk>/delete/",
        DepartmentDeleteView.as_view(),
        name="department_delete",
    ),
    path("employees/", EmployeeListView.as_view(), name="employee_list"),
    path(
        "employees/directory/",
        EmployeeDirectoryView.as_view(),
        name="employee_directory",
    ),
    path("employees/create/", EmployeeCreateView.as_view(), name="employee_create"),
    path("employees/me/", EmployeeProfileView.as_view(), name="employee_profile"),
    path("employees/<uuid:pk>/", EmployeeDetailView.as_view(), name="employee_detail"),
    path(
        "employees/<uuid:pk>/edit/",
        EmployeeUpdateView.as_view(),
        name="employee_update",
    ),
    path(
        "employees/<uuid:pk>/status/",
        EmployeeStatusUpdateView.as_view(),
        name="employee_status",
    ),
    path("hierarchy/", ReportingTreeView.as_view(), name="reporting_tree"),
    path("hierarchy/assign/", AssignManagerView.as_view(), name="assign_manager"),
    path(
        "hierarchy/<uuid:pk>/change/",
        ChangeManagerView.as_view(),
        name="change_manager",
    ),
    path(
        "organization/chart/",
        OrganizationChartView.as_view(),
        name="organization_chart",
    ),
]
