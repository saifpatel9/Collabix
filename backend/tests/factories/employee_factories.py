import factory

from apps.employees.models import (
    Department,
    EmployeeProfile,
)

from tests.factories.user_factories import UserFactory


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Department

    name = factory.Sequence(lambda n: f"Department {n}")
    description = "Test Department"


class EmployeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EmployeeProfile

    user = factory.SubFactory(UserFactory)
    employee_id = factory.Sequence(lambda n: f"EMP{n}")
    designation = "Developer"

    department = factory.SubFactory(DepartmentFactory)