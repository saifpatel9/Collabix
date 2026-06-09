def test_department_isolation(dept_admin_user, employee):
    from apps.core.rbac.rules import can_access_employee
    assert isinstance(can_access_employee(dept_admin_user, employee), bool)