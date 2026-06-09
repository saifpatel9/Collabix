import factory
from apps.tasks.models import Task
from .project_factories import ProjectFactory
from .employee_factories import EmployeeFactory


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    title = factory.Sequence(lambda n: f"Task {n}")
    task_code = factory.Sequence(lambda n: f"T{n}")
    project = factory.SubFactory(ProjectFactory)
    created_by = factory.SubFactory(EmployeeFactory)