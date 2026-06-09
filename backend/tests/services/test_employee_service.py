import pytest
from apps.employees.services.employee_service import EmployeeService
from django.core.exceptions import PermissionDenied


def test_employee_create_hr(hr_user):
    emp = EmployeeService.create(
        cleaned_data={
            "user_full_name": "Test",
            "user_email": "test@test.com",
            "user_role": "employee",
            "employee_id": "E1",
        },
        performed_by=hr_user,
    )
    assert emp.id is not None


def test_employee_create_denied(employee_user):
    with pytest.raises(PermissionDenied):
        EmployeeService.create(cleaned_data={}, performed_by=employee_user)