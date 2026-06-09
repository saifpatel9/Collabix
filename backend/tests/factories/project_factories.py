import factory
from apps.projects.models import Project, ProjectMember, Team
from tests.factories.user_factories import UserFactory
from tests.factories.employee_factories import EmployeeFactory


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Sequence(lambda n: f"Project {n}")
    code = factory.Sequence(lambda n: f"PRJ{n}")
    description = "Test project"

    owner = factory.SubFactory(EmployeeFactory)
    department = factory.LazyAttribute(lambda obj: obj.owner.department)

    status = Project.Status.PLANNING
    priority = Project.Priority.MEDIUM
    is_archived = False