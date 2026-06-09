import pytest
from apps.tasks.services.task_service import TaskService
from django.core.exceptions import PermissionDenied
from tests.factories.user_factories import UserFactory
from apps.accounts.models import User

def test_task_create_denied(employee_user, project):
    with pytest.raises(PermissionDenied):
        TaskService.create(
            cleaned_data={
                "title": "Test Task",
                "task_code": "T100",
                "project": project,
            },
            user=employee_user,
        )

def test_task_update_permission_denied(task):
    other_user = UserFactory(role=User.Role.EMPLOYEE)

    with pytest.raises(PermissionDenied):
        TaskService.update(
            task=task,
            cleaned_data={"title": "hack"},
            user=other_user,
        )