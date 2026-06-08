from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import TestCase

from apps.employees.models import Department, EmployeeProfile
from apps.employees.services.employee_service import EmployeeService


User = get_user_model()


class EmployeeAccessRBACTests(TestCase):
    def setUp(self):
        self.department_a = Department.objects.create(name="Engineering")
        self.department_b = Department.objects.create(name="Sales")

        self.manager_user = User.objects.create_user(
            email="mgr@example.com",
            full_name="Manager",
            password="testpass123",
            role=User.Role.MANAGER,
            must_change_password=False,
        )
        self.manager_employee = EmployeeProfile.objects.create(
            user=self.manager_user,
            employee_id="MGR001",
            designation="Manager",
            department=self.department_a,
        )

        self.direct_report_user = User.objects.create_user(
            email="report@example.com",
            full_name="Direct Report",
            password="testpass123",
            role=User.Role.EMPLOYEE,
            must_change_password=False,
        )
        self.direct_report_employee = EmployeeProfile.objects.create(
            user=self.direct_report_user,
            employee_id="REP001",
            designation="Engineer",
            department=self.department_a,
            manager=self.manager_employee,
        )

        self.unrelated_user = User.objects.create_user(
            email="unrelated-emp@example.com",
            full_name="Unrelated",
            password="testpass123",
            role=User.Role.EMPLOYEE,
            must_change_password=False,
        )
        self.unrelated_employee = EmployeeProfile.objects.create(
            user=self.unrelated_user,
            employee_id="UNR001",
            designation="Engineer",
            department=self.department_a,
        )

        self.department_admin_user = User.objects.create_user(
            email="deptadmin@example.com",
            full_name="Department Admin",
            password="testpass123",
            role=User.Role.DEPARTMENT_ADMIN,
            department=self.department_a.name,
            must_change_password=False,
        )
        self.department_admin_employee = EmployeeProfile.objects.create(
            user=self.department_admin_user,
            employee_id="DA001",
            designation="Department Admin",
            department=self.department_a,
        )

        self.other_department_user = User.objects.create_user(
            email="sales@example.com",
            full_name="Sales User",
            password="testpass123",
            role=User.Role.EMPLOYEE,
            must_change_password=False,
        )
        self.other_department_employee = EmployeeProfile.objects.create(
            user=self.other_department_user,
            employee_id="SAL001",
            designation="Sales",
            department=self.department_b,
        )

    def test_manager_cannot_edit_unrelated_employee(self):
        with self.assertRaises(PermissionDenied):
            EmployeeService.update(
                employee=self.unrelated_employee,
                cleaned_data={
                    "user_full_name": "Updated",
                    "user_email": "updated-unrelated@example.com",
                    "user_role": User.Role.EMPLOYEE,
                    "user_phone": "",
                },
                performed_by=self.manager_user,
            )

    def test_department_admin_limited_to_own_department(self):
        visible = EmployeeService.visible_to(self.department_admin_user)
        self.assertIn(self.unrelated_employee, visible)
        self.assertNotIn(self.other_department_employee, visible)

        with self.assertRaises(PermissionDenied):
            EmployeeService.update(
                employee=self.other_department_employee,
                cleaned_data={
                    "user_full_name": "Updated",
                    "user_email": "updated-sales@example.com",
                    "user_role": User.Role.EMPLOYEE,
                    "user_phone": "",
                },
                performed_by=self.department_admin_user,
            )

    def test_employee_can_only_access_self(self):
        with self.assertRaises(PermissionDenied):
            EmployeeService.update(
                employee=self.unrelated_employee,
                cleaned_data={
                    "user_full_name": "Updated",
                    "user_email": "updated-by-employee@example.com",
                    "user_role": User.Role.EMPLOYEE,
                    "user_phone": "",
                },
                performed_by=self.direct_report_user,
            )

