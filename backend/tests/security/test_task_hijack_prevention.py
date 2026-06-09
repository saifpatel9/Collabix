import pytest
from django.core.exceptions import PermissionDenied

from apps.accounts.models import User
from apps.tasks.services.task_service import TaskService
from tests.factories.user_factories import UserFactory
from tests.factories.employee_factories import EmployeeFactory


def test_task_hijack_prevent(task):
    attacker_user = UserFactory(role=User.Role.EMPLOYEE)
    EmployeeFactory(user=attacker_user)

    with pytest.raises(PermissionDenied):
        TaskService.update(
            task=task,
            cleaned_data={"title": "HACK"},
            user=attacker_user,
        )