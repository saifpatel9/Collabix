import pytest
from django.core.exceptions import PermissionDenied
from apps.projects.services.project_service import ProjectService


def test_project_create_admin(admin_user, admin_employee):
    project = ProjectService.create(
        cleaned_data={
            "name": "Test",
            "code": "T1",
            "owner": admin_employee,
            "department": admin_employee.department,
        },
        user=admin_user,
    )
    assert project.id is not None


def test_project_create_denied(employee_user):
    with pytest.raises(PermissionDenied):
        ProjectService.create(cleaned_data={}, user=employee_user)