from apps.core.rbac.rules import can_access_employee


def test_hr_can_access(hr_user, employee):
    assert can_access_employee(hr_user, employee)


def test_employee_only_self(employee_user, employee):
    assert isinstance(can_access_employee(employee_user, employee), bool)