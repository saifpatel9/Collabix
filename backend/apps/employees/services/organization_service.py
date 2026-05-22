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
    @transaction.atomic
    def upsert_position(*, cleaned_data):
        position, _ = OrganizationPosition.objects.update_or_create(
            employee=cleaned_data["employee"],
            defaults={
                "designation": cleaned_data["designation"],
                "department": cleaned_data["department"],
                "reporting_position": cleaned_data.get("reporting_position"),
            },
        )
        return position
