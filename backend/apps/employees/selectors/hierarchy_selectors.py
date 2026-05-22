from ..models import (
    Department,
    EmployeeHierarchy,
    EmployeeProfile,
    OrganizationPosition,
)


class HierarchySelector:
    @staticmethod
    def active_assignments():
        return EmployeeHierarchy.objects.select_related(
            "employee__user",
            "reporting_manager__user",
        ).filter(is_active=True)

    @staticmethod
    def employee_directory():
        return EmployeeProfile.objects.select_related(
            "user",
            "department",
            "manager__user",
        ).order_by("user__full_name")

    @staticmethod
    def positions_by_department(department: Department | None = None):
        queryset = OrganizationPosition.objects.select_related(
            "employee__user",
            "designation",
            "department",
            "reporting_position__employee__user",
        )
        if department:
            queryset = queryset.filter(department=department)
        return queryset
