from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from apps.employees.models import Department, EmployeeProfile
from apps.projects.models import Project
from apps.tasks.models import Task, TaskDependency
from apps.tasks.services.task_service import TaskService


User = get_user_model()


class TaskDependencyEnforcementTests(TestCase):
    def setUp(self):
        # Create a department
        self.department = Department.objects.create(name="Engineering")

        # Create a user and employee
        self.user = User.objects.create_user(
            email="testuser@example.com", full_name="Test User", password="testpass123"
        )
        self.employee = EmployeeProfile.objects.create(
            user=self.user, employee_id="EMP001"
        )

        # Create a project
        self.project = Project.objects.create(
            name="Test Project",
            code="PRJ001",
            owner=self.employee,
            department=self.department,
        )

        # Create predecessor task
        self.predecessor = Task.objects.create(
            project=self.project,
            title="Predecessor Task",
            task_code="TASK001",
            created_by=self.employee,
        )

        # Create successor task
        self.successor = Task.objects.create(
            project=self.project,
            title="Successor Task",
            task_code="TASK002",
            created_by=self.employee,
        )

    def test_start_to_start_blocked_when_predecessor_backlog(self):
        # Create start_to_start dependency
        TaskDependency.objects.create(
            predecessor_task=self.predecessor,
            successor_task=self.successor,
            dependency_type=TaskDependency.Type.START_TO_START,
        )

        # Try to move successor to IN_PROGRESS when predecessor is in BACKLOG
        with self.assertRaises(ValidationError):
            TaskService.change_status(task=self.successor, status=Task.Status.IN_PROGRESS)
        
        # Verify status remains unchanged
        self.successor.refresh_from_db()
        self.assertEqual(self.successor.status, Task.Status.BACKLOG)

    def test_start_to_start_allowed_when_predecessor_in_progress(self):
        TaskDependency.objects.create(
            predecessor_task=self.predecessor,
            successor_task=self.successor,
            dependency_type=TaskDependency.Type.START_TO_START,
        )
        
        # Move predecessor to IN_PROGRESS
        TaskService.change_status(task=self.predecessor, status=Task.Status.IN_PROGRESS)
        
        # Now try to move successor - should work
        TaskService.change_status(task=self.successor, status=Task.Status.IN_PROGRESS)
        
        self.successor.refresh_from_db()
        self.assertEqual(self.successor.status, Task.Status.IN_PROGRESS)

    def test_start_to_start_allowed_when_predecessor_completed(self):
        TaskDependency.objects.create(
            predecessor_task=self.predecessor,
            successor_task=self.successor,
            dependency_type=TaskDependency.Type.START_TO_START,
        )
        
        # Move predecessor to COMPLETED
        TaskService.change_status(task=self.predecessor, status=Task.Status.COMPLETED)
        
        # Now try to move successor - should work
        TaskService.change_status(task=self.successor, status=Task.Status.IN_PROGRESS)
        
        self.successor.refresh_from_db()
        self.assertEqual(self.successor.status, Task.Status.IN_PROGRESS)

    def test_finish_to_start_blocked_when_predecessor_incomplete(self):
        TaskDependency.objects.create(
            predecessor_task=self.predecessor,
            successor_task=self.successor,
            dependency_type=TaskDependency.Type.FINISH_TO_START,
        )
        
        # First move successor to IN_PROGRESS
        TaskService.change_status(task=self.successor, status=Task.Status.IN_PROGRESS)
        
        # Now try to move to COMPLETED when predecessor not completed
        with self.assertRaises(ValidationError):
            TaskService.change_status(task=self.successor, status=Task.Status.COMPLETED)
        
        # Verify status remains IN_PROGRESS
        self.successor.refresh_from_db()
        self.assertEqual(self.successor.status, Task.Status.IN_PROGRESS)

    def test_finish_to_start_allowed_when_predecessor_completed(self):
        TaskDependency.objects.create(
            predecessor_task=self.predecessor,
            successor_task=self.successor,
            dependency_type=TaskDependency.Type.FINISH_TO_START,
        )
        
        # First move successor to IN_PROGRESS
        TaskService.change_status(task=self.successor, status=Task.Status.IN_PROGRESS)
        
        # Move predecessor to COMPLETED
        TaskService.change_status(task=self.predecessor, status=Task.Status.COMPLETED)
        
        # Now try to complete successor
        TaskService.change_status(task=self.successor, status=Task.Status.COMPLETED)
        
        self.successor.refresh_from_db()
        self.assertEqual(self.successor.status, Task.Status.COMPLETED)

    def test_finish_to_finish_blocked_when_predecessor_incomplete(self):
        TaskDependency.objects.create(
            predecessor_task=self.predecessor,
            successor_task=self.successor,
            dependency_type=TaskDependency.Type.FINISH_TO_FINISH,
        )
        
        TaskService.change_status(task=self.successor, status=Task.Status.IN_PROGRESS)
        
        with self.assertRaises(ValidationError):
            TaskService.change_status(task=self.successor, status=Task.Status.COMPLETED)
        
        self.successor.refresh_from_db()
        self.assertEqual(self.successor.status, Task.Status.IN_PROGRESS)

    def test_finish_to_finish_allowed_when_predecessor_completed(self):
        TaskDependency.objects.create(
            predecessor_task=self.predecessor,
            successor_task=self.successor,
            dependency_type=TaskDependency.Type.FINISH_TO_FINISH,
        )
        
        TaskService.change_status(task=self.successor, status=Task.Status.IN_PROGRESS)
        TaskService.change_status(task=self.predecessor, status=Task.Status.COMPLETED)
        
        TaskService.change_status(task=self.successor, status=Task.Status.COMPLETED)
        
        self.successor.refresh_from_db()
        self.assertEqual(self.successor.status, Task.Status.COMPLETED)

    def test_multiple_dependencies_blocked(self):
        # Create second predecessor
        predecessor2 = Task.objects.create(
            project=self.project,
            title="Second Predecessor",
            task_code="TASK003",
            created_by=self.employee,
        )
        
        # Add both dependencies (start_to_start with first, finish_to_finish with second)
        TaskDependency.objects.create(
            predecessor_task=self.predecessor,
            successor_task=self.successor,
            dependency_type=TaskDependency.Type.START_TO_START,
        )
        TaskDependency.objects.create(
            predecessor_task=predecessor2,
            successor_task=self.successor,
            dependency_type=TaskDependency.Type.FINISH_TO_FINISH,
        )
        
        # First predecessor is in progress, second not completed
        TaskService.change_status(task=self.predecessor, status=Task.Status.IN_PROGRESS)
        
        # Try to move successor to IN_PROGRESS - okay for start_to_start, but when trying to complete
        TaskService.change_status(task=self.successor, status=Task.Status.IN_PROGRESS)
        
        with self.assertRaises(ValidationError):
            TaskService.change_status(task=self.successor, status=Task.Status.COMPLETED)
            
        self.successor.refresh_from_db()
        self.assertEqual(self.successor.status, Task.Status.IN_PROGRESS)

    def test_multiple_dependencies_allowed_when_all_satisfied(self):
        predecessor2 = Task.objects.create(
            project=self.project,
            title="Second Predecessor",
            task_code="TASK003",
            created_by=self.employee,
        )
        
        TaskDependency.objects.create(
            predecessor_task=self.predecessor,
            successor_task=self.successor,
            dependency_type=TaskDependency.Type.START_TO_START,
        )
        TaskDependency.objects.create(
            predecessor_task=predecessor2,
            successor_task=self.successor,
            dependency_type=TaskDependency.Type.FINISH_TO_FINISH,
        )
        
        # Satisfy both dependencies
        TaskService.change_status(task=self.predecessor, status=Task.Status.IN_PROGRESS)
        TaskService.change_status(task=predecessor2, status=Task.Status.COMPLETED)
        
        TaskService.change_status(task=self.successor, status=Task.Status.IN_PROGRESS)
        TaskService.change_status(task=self.successor, status=Task.Status.COMPLETED)
        
        self.successor.refresh_from_db()
        self.assertEqual(self.successor.status, Task.Status.COMPLETED)

    def test_no_dependencies_allowed(self):
        # No dependencies, any status change should work
        TaskService.change_status(task=self.successor, status=Task.Status.IN_PROGRESS)
        TaskService.change_status(task=self.successor, status=Task.Status.REVIEW)
        TaskService.change_status(task=self.successor, status=Task.Status.COMPLETED)
        
        self.successor.refresh_from_db()
        self.assertEqual(self.successor.status, Task.Status.COMPLETED)
