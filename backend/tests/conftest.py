import pytest
from apps.accounts.models import User
from tests.factories.user_factories import UserFactory
from tests.factories.employee_factories import EmployeeFactory
from tests.factories.project_factories import ProjectFactory
from tests.factories.task_factories import TaskFactory


@pytest.fixture
def admin_user(db):
    return UserFactory(role=User.Role.ADMIN)


@pytest.fixture
def hr_user(db):
    return UserFactory(role=User.Role.HR_MANAGER)


@pytest.fixture
def dept_admin_user(db):
    return UserFactory(role=User.Role.DEPARTMENT_ADMIN)


@pytest.fixture
def manager_user(db):
    return UserFactory(role=User.Role.MANAGER)


@pytest.fixture
def employee_user(db):
    return UserFactory(role=User.Role.EMPLOYEE)


@pytest.fixture
def employee(employee_user):
    return EmployeeFactory(user=employee_user)


@pytest.fixture
def manager_employee(manager_user):
    return EmployeeFactory(user=manager_user)


@pytest.fixture
def project(admin_user, employee):
    return ProjectFactory(owner=employee)


@pytest.fixture
def task(project, employee):
    return TaskFactory(project=project, created_by=employee)

@pytest.fixture
def admin_employee(admin_user):
    return EmployeeFactory(user=admin_user)