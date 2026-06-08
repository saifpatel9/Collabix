from django.test import TestCase

from apps.accounts.models import User
from apps.core.rbac.rules import (
    can_access_employee,
)
from apps.employees.models import Department, EmployeeProfile


class CanAccessEmployeeRuleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.engineering = Department.objects.create(name="Engineering")
        cls.hr = Department.objects.create(name="HR")

        cls.admin_user = User.objects.create_user(
            email="admin@test.com",
            password="testpass123",
            full_name="Admin User",
            role=User.Role.ADMIN,
        )

        cls.hr_user = User.objects.create_user(
            email="hr@test.com",
            password="testpass123",
            full_name="HR User",
            role=User.Role.HR_MANAGER,
        )

        cls.manager_user = User.objects.create_user(
            email="manager@test.com",
            password="testpass123",
            full_name="Manager User",
            role=User.Role.MANAGER,
        )

        cls.department_admin_user = User.objects.create_user(
            email="deptadmin@test.com",
            password="testpass123",
            full_name="Department Admin",
            role=User.Role.DEPARTMENT_ADMIN,
        )

        cls.employee_user = User.objects.create_user(
            email="employee@test.com",
            password="testpass123",
            full_name="Employee User",
            role=User.Role.EMPLOYEE,
        )

        cls.other_employee_user = User.objects.create_user(
            email="other@test.com",
            password="testpass123",
            full_name="Other Employee",
            role=User.Role.EMPLOYEE,
        )

        cls.manager_profile = EmployeeProfile.objects.create(
            user=cls.manager_user,
            employee_id="EMP001",
            department=cls.engineering,
        )

        cls.department_admin_profile = EmployeeProfile.objects.create(
            user=cls.department_admin_user,
            employee_id="EMP002",
            department=cls.engineering,
        )

        cls.employee_profile = EmployeeProfile.objects.create(
            user=cls.employee_user,
            employee_id="EMP003",
            department=cls.engineering,
            manager=cls.manager_profile,
        )

        cls.other_employee_profile = EmployeeProfile.objects.create(
            user=cls.other_employee_user,
            employee_id="EMP004",
            department=cls.hr,
        )

    def test_admin_can_access_any_employee(self):
        self.assertTrue(
            can_access_employee(
                self.admin_user,
                self.employee_profile,
            )
        )

    def test_hr_manager_can_access_any_employee(self):
        self.assertTrue(
            can_access_employee(
                self.hr_user,
                self.employee_profile,
            )
        )

    def test_department_admin_can_access_same_department_employee(self):
        self.assertTrue(
            can_access_employee(
                self.department_admin_user,
                self.employee_profile,
            )
        )

    def test_department_admin_cannot_access_other_department_employee(self):
        self.assertFalse(
            can_access_employee(
                self.department_admin_user,
                self.other_employee_profile,
            )
        )

    def test_manager_can_access_direct_report(self):
        self.assertTrue(
            can_access_employee(
                self.manager_user,
                self.employee_profile,
            )
        )

    def test_manager_cannot_access_unrelated_employee(self):
        self.assertFalse(
            can_access_employee(
                self.manager_user,
                self.other_employee_profile,
            )
        )

    def test_employee_can_access_self(self):
        self.assertTrue(
            can_access_employee(
                self.employee_user,
                self.employee_profile,
            )
        )

    def test_employee_cannot_access_other_employee(self):
        self.assertFalse(
            can_access_employee(
                self.employee_user,
                self.other_employee_profile,
            )
        )