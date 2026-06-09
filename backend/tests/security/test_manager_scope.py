from apps.accounts.models import User
from apps.core.rbac.rules import can_edit_task
from tests.factories.employee_factories import EmployeeFactory
from tests.factories.user_factories import UserFactory


def test_manager_cannot_hijack_unrelated_task(db, task):
    manager_user = UserFactory(role=User.Role.MANAGER)

    EmployeeFactory(user=manager_user)

    assert can_edit_task(manager_user, task) is False