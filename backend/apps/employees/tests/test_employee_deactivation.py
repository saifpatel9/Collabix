from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from apps.employees.models import Department, EmployeeProfile
from apps.employees.services.employee_service import EmployeeService


User = get_user_model()


class EmployeeDeactivationTests(TestCase):
    def setUp(self):
        # Create a department
        self.department = Department.objects.create(name="Engineering")
        
        # Create HR manager
        self.hr_user = User.objects.create_user(
            email="hr@example.com",
            full_name="HR Manager",
            password="testpass123",
            role=User.Role.HR_MANAGER
        )
        self.hr_employee = EmployeeProfile.objects.create(
            user=self.hr_user,
            employee_id="HR001",
            designation="HR Manager",
            department=self.department
        )
        
        # Create regular employee
        self.employee_user = User.objects.create_user(
            email="employee@example.com",
            full_name="Test Employee",
            password="testpass123",
            role=User.Role.EMPLOYEE
        )
        self.employee = EmployeeProfile.objects.create(
            user=self.employee_user,
            employee_id="EMP001",
            designation="Software Engineer",
            department=self.department
        )
        
        # Create superuser
        self.super_user = User.objects.create_superuser(
            email="superuser@example.com",
            full_name="Super User",
            password="testpass123"
        )
        self.super_employee = EmployeeProfile.objects.create(
            user=self.super_user,
            employee_id="SUPER001",
            designation="Superuser",
            department=self.department
        )
        
    def test_successful_deactivation(self):
        # Test successful deactivation
        EmployeeService.deactivate(
            employee=self.employee,
            performed_by=self.hr_user
        )
        
        # Refresh from db
        self.employee.refresh_from_db()
        self.employee_user.refresh_from_db()
        
        # Check statuses
        self.assertEqual(self.employee.employment_status, EmployeeProfile.EmploymentStatus.INACTIVE)
        self.assertFalse(self.employee_user.is_active)
        
        # Check that employee still exists
        self.assertTrue(EmployeeProfile.objects.filter(pk=self.employee.pk).exists())
        
    def test_cannot_deactivate_superuser(self):
        # Test trying to deactivate superuser raises error
        with self.assertRaises(ValidationError) as ctx:
            EmployeeService.deactivate(
                employee=self.super_employee,
                performed_by=self.hr_user
            )
        self.assertIn("Cannot deactivate a superuser", str(ctx.exception))
        
    def test_cannot_deactivate_self(self):
        # Test trying to deactivate self raises error
        with self.assertRaises(ValidationError) as ctx:
            EmployeeService.deactivate(
                employee=self.hr_employee,
                performed_by=self.hr_user
            )
        self.assertIn("You cannot deactivate yourself", str(ctx.exception))
        
    def test_cannot_deactivate_already_inactive(self):
        # First deactivate
        EmployeeService.deactivate(
            employee=self.employee,
            performed_by=self.hr_user
        )
        
        # Now try again
        with self.assertRaises(ValidationError) as ctx:
            EmployeeService.deactivate(
                employee=self.employee,
                performed_by=self.hr_user
            )
        self.assertIn("This employee is already inactive", str(ctx.exception))
        
    def test_filtering_defaults_to_active(self):
        # Deactivate employee
        EmployeeService.deactivate(
            employee=self.employee,
            performed_by=self.hr_user
        )
        
        # Get all employees
        visible = EmployeeService.visible_to(self.hr_user)
        filtered = EmployeeService.search_and_filter(visible)
        
        # Should not see inactive employee
        self.assertNotIn(self.employee, filtered)
        
    def test_can_see_inactive_when_filtered(self):
        # Deactivate employee
        EmployeeService.deactivate(
            employee=self.employee,
            performed_by=self.hr_user
        )
        
        visible = EmployeeService.visible_to(self.hr_user)
        filtered = EmployeeService.search_and_filter(
            visible, 
            employment_status=EmployeeProfile.EmploymentStatus.INACTIVE
        )
        
        self.assertIn(self.employee, filtered)
        
    def test_inactive_user_cannot_login(self):
        # Deactivate
        EmployeeService.deactivate(
            employee=self.employee,
            performed_by=self.hr_user
        )
        
        # Test login fails
        logged_in = self.client.login(
            email="employee@example.com",
            password="testpass123"
        )
        self.assertFalse(logged_in)
