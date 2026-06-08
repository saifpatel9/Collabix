from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import TestCase

from apps.employees.models import Department, EmployeeProfile
from apps.projects.models import Project, ProjectMember
from apps.projects.services.project_service import ProjectService


User = get_user_model()


class ProjectRBACTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Engineering")

        self.project_manager_user = User.objects.create_user(
            email="pm@example.com",
            full_name="Project Manager",
            password="testpass123",
            role=User.Role.PROJECT_MANAGER,
            must_change_password=False,
        )
        self.project_manager_employee = EmployeeProfile.objects.create(
            user=self.project_manager_user,
            employee_id="PM001",
            designation="PM",
            department=self.department,
        )

        self.owner_user = User.objects.create_user(
            email="owner@example.com",
            full_name="Owner",
            password="testpass123",
            role=User.Role.EMPLOYEE,
            must_change_password=False,
        )
        self.owner_employee = EmployeeProfile.objects.create(
            user=self.owner_user,
            employee_id="OWN001",
            designation="Owner",
            department=self.department,
        )

        self.contributor_user = User.objects.create_user(
            email="contrib@example.com",
            full_name="Contributor",
            password="testpass123",
            role=User.Role.EMPLOYEE,
            must_change_password=False,
        )
        self.contributor_employee = EmployeeProfile.objects.create(
            user=self.contributor_user,
            employee_id="CON001",
            designation="Contributor",
            department=self.department,
        )

        self.unrelated_user = User.objects.create_user(
            email="unrelated@example.com",
            full_name="Unrelated",
            password="testpass123",
            role=User.Role.EMPLOYEE,
            must_change_password=False,
        )
        self.unrelated_employee = EmployeeProfile.objects.create(
            user=self.unrelated_user,
            employee_id="UNR001",
            designation="Employee",
            department=self.department,
        )

        self.project = Project.objects.create(
            name="Project A",
            code="PRJ-A",
            owner=self.owner_employee,
            department=self.department,
        )
        ProjectMember.objects.create(
            project=self.project,
            employee=self.contributor_employee,
            role=ProjectMember.Role.CONTRIBUTOR,
        )

    def test_employee_cannot_edit_unauthorized_project(self):
        with self.assertRaises(PermissionDenied):
            ProjectService.update(
                project=self.project,
                cleaned_data={"name": "New Name"},
                user=self.unrelated_user,
            )

    def test_contributor_cannot_archive_project(self):
        with self.assertRaises(PermissionDenied):
            ProjectService.archive(project=self.project, user=self.contributor_user)

    def test_project_manager_can_manage_project(self):
        ProjectService.update(
            project=self.project,
            cleaned_data={"name": "Updated by PM"},
            user=self.project_manager_user,
        )
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Updated by PM")

        ProjectService.archive(project=self.project, user=self.project_manager_user)
        self.project.refresh_from_db()
        self.assertTrue(self.project.is_archived)

