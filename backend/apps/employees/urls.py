from django.urls import path

from .views import (
    AssignManagerView,
    ChangeManagerView,
    DepartmentCreateView,
    DepartmentDeleteView,
    DepartmentDetailView,
    DepartmentListView,
    DepartmentUpdateView,
    DesignationCreateView,
    DesignationDeleteView,
    DesignationDetailView,
    DesignationListView,
    DesignationUpdateView,
    EmployeeCreateView,
    EmployeeDetailView,
    EmployeeDirectoryView,
    EmployeeListView,
    EmployeeProfileView,
    EmployeeStatusUpdateView,
    EmployeeUpdateView,
    OrganizationChartView,
    OrganizationPositionCreateView,
    OrganizationPositionDeleteView,
    OrganizationPositionListView,
    OrganizationPositionUpdateView,
    ReportingTreeView,
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
    path("designations/", DesignationListView.as_view(), name="designation_list"),
    path(
        "designations/create/", DesignationCreateView.as_view(), name="designation_create"
    ),
    path(
        "designations/<uuid:pk>/",
        DesignationDetailView.as_view(),
        name="designation_detail",
    ),
    path(
        "designations/<uuid:pk>/edit/",
        DesignationUpdateView.as_view(),
        name="designation_update",
    ),
    path(
        "designations/<uuid:pk>/delete/",
        DesignationDeleteView.as_view(),
        name="designation_delete",
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
    path(
        "organization/positions/",
        OrganizationPositionListView.as_view(),
        name="organization_position_list",
    ),
    path(
        "organization/positions/create/",
        OrganizationPositionCreateView.as_view(),
        name="organization_position_create",
    ),
    path(
        "organization/positions/<uuid:pk>/edit/",
        OrganizationPositionUpdateView.as_view(),
        name="organization_position_update",
    ),
    path(
        "organization/positions/<uuid:pk>/delete/",
        OrganizationPositionDeleteView.as_view(),
        name="organization_position_delete",
    ),
]
