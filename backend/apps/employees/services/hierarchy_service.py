from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from ..models import EmployeeHierarchy, EmployeeProfile


class EmployeeHierarchyService:
    @staticmethod
    def active_queryset():
        return EmployeeHierarchy.objects.select_related(
            "employee__user",
            "employee__department",
            "reporting_manager__user",
        ).filter(is_active=True)

    @staticmethod
    def validate_assignment(*, employee, reporting_manager):
        if employee.pk == reporting_manager.pk:
            raise ValidationError("Employee cannot report to self.")
        if EmployeeHierarchyService._creates_cycle(
            employee=employee,
            reporting_manager=reporting_manager,
        ):
            raise ValidationError("This assignment creates a circular reporting chain.")

    @staticmethod
    @transaction.atomic
    def assign_manager(*, employee, reporting_manager, effective_from=None):
        EmployeeHierarchyService.validate_assignment(
            employee=employee,
            reporting_manager=reporting_manager,
        )
        effective_from = effective_from or timezone.localdate()
        EmployeeHierarchy.objects.filter(employee=employee, is_active=True).update(
            is_active=False,
            effective_to=effective_from,
        )
        employee.manager = reporting_manager
        employee.save(update_fields=["manager", "updated_at"])
        return EmployeeHierarchy.objects.create(
            employee=employee,
            reporting_manager=reporting_manager,
            effective_from=effective_from,
            is_active=True,
        )

    @staticmethod
    def reporting_tree(root_manager=None):
        assignments = EmployeeHierarchyService.active_queryset()
        if root_manager:
            assignments = assignments.filter(reporting_manager=root_manager)
        return assignments.order_by(
            "reporting_manager__user__full_name", "employee__user__full_name"
        )

    @staticmethod
    def directory_queryset():
        return EmployeeProfile.objects.select_related(
            "user", "department", "manager__user"
        ).order_by("user__full_name")

    @staticmethod
    def _creates_cycle(*, employee, reporting_manager):
        visited = {employee.pk}
        current = reporting_manager
        while current:
            if current.pk in visited:
                return True
            visited.add(current.pk)
            active = (
                EmployeeHierarchy.objects.select_related("reporting_manager")
                .filter(employee=current, is_active=True)
                .first()
            )
            current = active.reporting_manager if active else None
        return False
