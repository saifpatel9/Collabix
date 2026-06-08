from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import TestCase

from apps.employees.models import Department, EmployeeProfile
from apps.projects.models import Project, ProjectMember
from apps.tasks.models import Task, TaskAssignment
from apps.tasks.services.task_service import TaskService


User = get_user_model()


class TaskRBACTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Engineering")

        self.owner_user = User.objects.create_user(
            email="owner-task@example.com",
            full_name="Owner",
            password="testpass123",
            role=User.Role.EMPLOYEE,
            must_change_password=False,
        )
        self.owner_employee = EmployeeProfile.objects.create(
            user=self.owner_user,
            employee_id="OWN-TASK",
            designation="Owner",
            department=self.department,
        )

        self.assignee_user = User.objects.create_user(
            email="assignee@example.com",
            full_name="Assignee",
            password="testpass123",
            role=User.Role.EMPLOYEE,
            must_change_password=False,
        )
        self.assignee_employee = EmployeeProfile.objects.create(
            user=self.assignee_user,
            employee_id="ASG001",
            designation="Engineer",
            department=self.department,
        )

        self.unrelated_user = User.objects.create_user(
            email="unrelated-task@example.com",
            full_name="Unrelated",
            password="testpass123",
            role=User.Role.EMPLOYEE,
            must_change_password=False,
        )
        self.unrelated_employee = EmployeeProfile.objects.create(
            user=self.unrelated_user,
            employee_id="UNR-TASK",
            designation="Engineer",
            department=self.department,
        )

        self.project = Project.objects.create(
            name="Task Project",
            code="TPRJ1",
            owner=self.owner_employee,
            department=self.department,
        )

        ProjectMember.objects.create(
            project=self.project,
            employee=self.assignee_employee,
            role=ProjectMember.Role.CONTRIBUTOR,
        )

        self.task = Task.objects.create(
            project=self.project,
            title="Task 1",
            task_code="TASK-RBAC-1",
            created_by=self.owner_employee,
        )
        TaskAssignment.objects.create(
            task=self.task,
            employee=self.assignee_employee,
            assigned_by=self.owner_employee,
        )

    def test_assignee_can_update_status(self):
        TaskService.change_status(
            task=self.task,
            status=Task.Status.IN_PROGRESS,
            user=self.assignee_user,
        )
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, Task.Status.IN_PROGRESS)

    def test_unauthorized_employee_blocked_from_edit(self):
        with self.assertRaises(PermissionDenied):
            TaskService.update(
                task=self.task,
                cleaned_data={"title": "Hacked"},
                user=self.unrelated_user,
            )

