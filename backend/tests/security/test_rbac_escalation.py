def test_employee_cannot_be_admin(employee_user, project):
    from apps.core.rbac.rules import can_manage_project
    assert not can_manage_project(employee_user, project)