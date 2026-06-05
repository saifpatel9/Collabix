from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.employees.models import (
    Department,
    Designation,
    EmployeeProfile,
    OrganizationPosition,
)
from apps.employees.services.designation_service import DesignationService
from apps.employees.services.organization_service import OrganizationService

User = get_user_model()


class DesignationModelTests(TestCase):
    def setUp(self):
        self.designation = Designation.objects.create(
            title="Software Engineer", level=3, description="Senior software engineer role"
        )

    def test_designation_creation(self):
        self.assertEqual(self.designation.title, "Software Engineer")
        self.assertEqual(self.designation.level, 3)
        self.assertIsNotNone(self.designation.created_at)

    def test_designation_str(self):
        self.assertEqual(str(self.designation), "Software Engineer")

    def test_unique_title(self):
        with self.assertRaises(Exception):
            Designation.objects.create(title="Software Engineer", level=2)


class DesignationServiceTests(TestCase):
    def setUp(self):
        self.designation1 = Designation.objects.create(title="CEO", level=1)
        self.designation2 = Designation.objects.create(title="Manager", level=2)
        self.designation3 = Designation.objects.create(title="Developer", level=3)

    def test_all_designations(self):
        designations = DesignationService.all_designations()
        self.assertEqual(designations.count(), 3)

    def test_search_by_title(self):
        queryset = Designation.objects.all()
        results = DesignationService.search(queryset, "CEO")
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().title, "CEO")

    def test_search_by_description(self):
        desc_designation = Designation.objects.create(
            title="HR Manager", level=2, description="Human resources management"
        )
        queryset = Designation.objects.all()
        results = DesignationService.search(queryset, "resources")
        self.assertEqual(results.count(), 1)

    def test_create_designation(self):
        new_designation = DesignationService.create(
            cleaned_data={
                "title": "Director",
                "level": 2,
                "description": "Director role",
            }
        )
        self.assertEqual(new_designation.title, "Director")
        self.assertTrue(Designation.objects.filter(title="Director").exists())

    def test_update_designation(self):
        DesignationService.update(
            designation=self.designation1,
            cleaned_data={"title": "Chief Executive Officer", "level": 1, "description": ""},
        )
        self.designation1.refresh_from_db()
        self.assertEqual(self.designation1.title, "Chief Executive Officer")

    def test_delete_designation(self):
        designation_id = self.designation1.id
        DesignationService.delete(designation=self.designation1)
        self.assertFalse(Designation.objects.filter(id=designation_id).exists())


class OrganizationPositionModelTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Engineering")
        self.designation = Designation.objects.create(title="CEO", level=1)

        self.user1 = User.objects.create_user(
            email="john@example.com", full_name="John Smith", password="testpass"
        )
        self.employee1 = EmployeeProfile.objects.create(
            user=self.user1, employee_id="EMP001", designation="CEO"
        )

    def test_position_creation(self):
        position = OrganizationPosition.objects.create(
            employee=self.employee1,
            designation=self.designation,
            department=self.department,
        )
        self.assertEqual(position.employee, self.employee1)
        self.assertEqual(position.designation, self.designation)
        self.assertIsNone(position.reporting_position)

    def test_self_reporting_prevention(self):
        position = OrganizationPosition.objects.create(
            employee=self.employee1,
            designation=self.designation,
            department=self.department,
        )
        position.reporting_position = position
        with self.assertRaises(ValidationError):
            position.clean()

    def test_unique_employee_constraint(self):
        OrganizationPosition.objects.create(
            employee=self.employee1,
            designation=self.designation,
            department=self.department,
        )
        # Attempting to create another position for same employee should raise error
        with self.assertRaises(Exception):
            OrganizationPosition.objects.create(
                employee=self.employee1,
                designation=self.designation,
                department=self.department,
            )


class OrganizationPositionServiceTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="Engineering")
        self.designation_ceo = Designation.objects.create(title="CEO", level=1)
        self.designation_cto = Designation.objects.create(title="CTO", level=2)
        self.designation_dev = Designation.objects.create(title="Developer", level=3)

        self.user_ceo = User.objects.create_user(
            email="ceo@example.com", full_name="John CEO", password="testpass"
        )
        self.employee_ceo = EmployeeProfile.objects.create(
            user=self.user_ceo, employee_id="EMP001"
        )

        self.user_cto = User.objects.create_user(
            email="cto@example.com", full_name="Jane CTO", password="testpass"
        )
        self.employee_cto = EmployeeProfile.objects.create(
            user=self.user_cto, employee_id="EMP002"
        )

        self.user_dev = User.objects.create_user(
            email="dev@example.com", full_name="Bob Dev", password="testpass"
        )
        self.employee_dev = EmployeeProfile.objects.create(
            user=self.user_dev, employee_id="EMP003"
        )

    def test_create_root_position(self):
        position = OrganizationService.create_position(
            cleaned_data={
                "employee": self.employee_ceo,
                "designation": self.designation_ceo,
                "department": self.department,
            }
        )
        self.assertIsNone(position.reporting_position)

    def test_create_child_position(self):
        root_position = OrganizationPosition.objects.create(
            employee=self.employee_ceo,
            designation=self.designation_ceo,
            department=self.department,
        )

        child_position = OrganizationService.create_position(
            cleaned_data={
                "employee": self.employee_cto,
                "designation": self.designation_cto,
                "department": self.department,
                "reporting_position": root_position,
            }
        )
        self.assertEqual(child_position.reporting_position, root_position)

    def test_self_reporting_validation(self):
        ceo_position = OrganizationPosition.objects.create(
            employee=self.employee_ceo,
            designation=self.designation_ceo,
            department=self.department,
        )

        with self.assertRaises(ValidationError):
            OrganizationService.validate_position(
                employee=self.employee_ceo,
                reporting_position=ceo_position,
            )

    def test_circular_reporting_detection(self):
        # Create a chain: CEO -> CTO -> Developer
        ceo_position = OrganizationPosition.objects.create(
            employee=self.employee_ceo,
            designation=self.designation_ceo,
            department=self.department,
        )

        cto_position = OrganizationPosition.objects.create(
            employee=self.employee_cto,
            designation=self.designation_cto,
            department=self.department,
            reporting_position=ceo_position,
        )

        dev_position = OrganizationPosition.objects.create(
            employee=self.employee_dev,
            designation=self.designation_dev,
            department=self.department,
            reporting_position=cto_position,
        )

        # Try to create a circular relationship: CEO reports to Developer
        with self.assertRaises(ValidationError):
            OrganizationService.validate_position(
                employee=self.employee_ceo, reporting_position=dev_position
            )

    def test_has_circular_reporting(self):
        ceo_position = OrganizationPosition.objects.create(
            employee=self.employee_ceo,
            designation=self.designation_ceo,
            department=self.department,
        )

        cto_position = OrganizationPosition.objects.create(
            employee=self.employee_cto,
            designation=self.designation_cto,
            department=self.department,
            reporting_position=ceo_position,
        )

        # Should detect cycle
        is_circular = OrganizationService.has_circular_reporting(
            ceo_position.pk, cto_position.pk
        )
        self.assertTrue(is_circular)

    def test_build_org_tree(self):
        ceo_position = OrganizationPosition.objects.create(
            employee=self.employee_ceo,
            designation=self.designation_ceo,
            department=self.department,
        )

        cto_position = OrganizationPosition.objects.create(
            employee=self.employee_cto,
            designation=self.designation_cto,
            department=self.department,
            reporting_position=ceo_position,
        )

        tree = OrganizationService.build_org_tree()
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[0]["position"].employee, self.employee_ceo)
        self.assertEqual(len(tree[0]["children"]), 1)
        self.assertEqual(tree[0]["children"][0]["position"].employee, self.employee_cto)

    def test_update_position(self):
        position = OrganizationPosition.objects.create(
            employee=self.employee_ceo,
            designation=self.designation_ceo,
            department=self.department,
        )

        updated = OrganizationService.update_position(
            position=position,
            cleaned_data={
                "designation": self.designation_cto,
                "department": self.department,
                "reporting_position": None,
            },
        )
        position.refresh_from_db()
        self.assertEqual(position.designation, self.designation_cto)

    def test_delete_position(self):
        position = OrganizationPosition.objects.create(
            employee=self.employee_ceo,
            designation=self.designation_ceo,
            department=self.department,
        )
        position_id = position.id
        OrganizationService.delete_position(position=position)
        self.assertFalse(OrganizationPosition.objects.filter(id=position_id).exists())


class DesignationViewTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            full_name="Admin User",
            password="testpass",
            role="admin",
        )
        self.designation1 = Designation.objects.create(title="CEO", level=1)
        self.designation2 = Designation.objects.create(title="Manager", level=2)

    def test_designation_list_view(self):
        self.client.login(email="admin@example.com", password="testpass")
        response = self.client.get(reverse("employees:designation_list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("designations", response.context)

    def test_designation_create_view(self):
        self.client.login(email="admin@example.com", password="testpass")
        data = {"title": "Director", "level": 2, "description": "Director role"}
        response = self.client.post(reverse("employees:designation_create"), data)
        self.assertTrue(Designation.objects.filter(title="Director").exists())

    def test_designation_update_view(self):
        self.client.login(email="admin@example.com", password="testpass")
        data = {"title": "Chief Executive Officer", "level": 1, "description": "CEO"}
        response = self.client.post(
            reverse("employees:designation_update", args=[self.designation1.pk]), data
        )
        self.designation1.refresh_from_db()
        self.assertEqual(self.designation1.title, "Chief Executive Officer")

    def test_designation_delete_view(self):
        self.client.login(email="admin@example.com", password="testpass")
        designation_id = self.designation1.pk
        response = self.client.post(
            reverse("employees:designation_delete", args=[designation_id])
        )
        self.assertFalse(Designation.objects.filter(id=designation_id).exists())
