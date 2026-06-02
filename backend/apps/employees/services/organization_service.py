from django.core.exceptions import ValidationError
from django.db import transaction

from ..models import Designation, OrganizationPosition


class OrganizationService:
    @staticmethod
    def designations():
        return Designation.objects.order_by("level", "title")

    @staticmethod
    def positions_for_department(department=None):
        queryset = OrganizationPosition.objects.select_related(
            "employee__user",
            "designation",
            "department",
            "reporting_position__employee__user",
        )
        if department:
            queryset = queryset.filter(department=department)
        return queryset.order_by(
            "department__name", "designation__level", "employee__user__full_name"
        )

    @staticmethod
    def get_root_positions(department=None):
        queryset = OrganizationPosition.objects.filter(
            reporting_position__isnull=True
        ).select_related("employee__user", "designation", "department")
        if department:
            queryset = queryset.filter(department=department)
        return queryset

    @staticmethod
    def build_org_tree(position=None, department=None):
        if position is None:
            root_positions = OrganizationService.get_root_positions(department)
            return [
                {
                    "position": pos,
                    "children": OrganizationService.build_org_tree(pos, department),
                }
                for pos in root_positions
            ]

        child_positions = OrganizationPosition.objects.filter(
            reporting_position=position
        ).select_related("employee__user", "designation", "department")

        return [
            {
                "position": child,
                "children": OrganizationService.build_org_tree(child, department),
            }
            for child in child_positions
        ]

    @staticmethod
    def has_circular_reporting(position_id, reporting_position_id):
        if position_id == reporting_position_id:
            return True

        if not reporting_position_id:
            return False

        visited = set()
        current = reporting_position_id

        while current:
            if current in visited:
                return True
            visited.add(current)

            try:
                parent = OrganizationPosition.objects.get(
                    pk=current
                ).reporting_position_id
                current = parent
            except OrganizationPosition.DoesNotExist:
                break

        return False

    @staticmethod
    def validate_position(*, employee, reporting_position):
        if reporting_position and employee.pk == reporting_position.employee_id:
            raise ValidationError("An employee cannot report to themselves.")

        if reporting_position:
            if OrganizationService.has_circular_reporting(
                employee.pk, reporting_position.pk
            ):
                raise ValidationError(
                    "This would create a circular reporting relationship."
                )

    @staticmethod
    @transaction.atomic
    def upsert_position(*, cleaned_data):
        employee = cleaned_data["employee"]
        reporting_position = cleaned_data.get("reporting_position")

        OrganizationService.validate_position(
            employee=employee, reporting_position=reporting_position
        )

        position, _ = OrganizationPosition.objects.update_or_create(
            employee=employee,
            defaults={
                "designation": cleaned_data["designation"],
                "department": cleaned_data["department"],
                "reporting_position": reporting_position,
            },
        )
        return position

    @staticmethod
    @transaction.atomic
    def create_position(*, cleaned_data):
        employee = cleaned_data["employee"]
        reporting_position = cleaned_data.get("reporting_position")

        OrganizationService.validate_position(
            employee=employee, reporting_position=reporting_position
        )

        return OrganizationPosition.objects.create(**cleaned_data)

    @staticmethod
    @transaction.atomic
    def update_position(*, position, cleaned_data):
        reporting_position = cleaned_data.get("reporting_position")

        OrganizationService.validate_position(
            employee=position.employee, reporting_position=reporting_position
        )

        for field, value in cleaned_data.items():
            setattr(position, field, value)
        position.save()
        return position

    @staticmethod
    @transaction.atomic
    def delete_position(*, position):
        position.delete()
