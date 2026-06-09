from apps.core.rbac.rules import can_manage_project


def test_admin_can_manage_project(admin_user, project):
    assert can_manage_project(admin_user, project)


def test_employee_cannot_manage_project(employee_user, project):
    assert not can_manage_project(employee_user, project)