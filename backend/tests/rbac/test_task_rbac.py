from apps.core.rbac.rules import can_execute_task, can_edit_task
from apps.accounts.models import User
from apps.core.rbac.rules import (
    can_execute_task,
    can_edit_task,
    can_view_task,
)
from tests.factories.user_factories import UserFactory
from tests.factories.employee_factories import EmployeeFactory

def test_assignee_can_execute(employee_user, task):
    assert isinstance(can_execute_task(employee_user, task), bool)


def test_employee_cannot_edit_task(employee_user, task):
    assert isinstance(can_edit_task(employee_user, task), bool)

def test_manager_can_view_direct_report_task(db, task):
    manager_user = UserFactory(role=User.Role.MANAGER)

    manager_employee = EmployeeFactory(
        user=manager_user,
    )

    task.created_by.manager = manager_employee
    task.created_by.save()

    assert can_view_task(manager_user, task) is True

def test_manager_can_manage_direct_report_task(db, task):
    manager_user = UserFactory(role=User.Role.MANAGER)

    manager_employee = EmployeeFactory(
        user=manager_user,
    )

    task.created_by.manager = manager_employee
    task.created_by.save()

    assert can_edit_task(manager_user, task) is True

def test_manager_cannot_view_unrelated_task(db, task):
    manager_user = UserFactory(role=User.Role.MANAGER)

    EmployeeFactory(user=manager_user)

    assert can_view_task(manager_user, task) is False

def test_manager_cannot_manage_unrelated_task(db, task):
    manager_user = UserFactory(role=User.Role.MANAGER)

    EmployeeFactory(user=manager_user)

    assert can_edit_task(manager_user, task) is False    