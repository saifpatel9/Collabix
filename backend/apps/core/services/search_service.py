from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.employees.models import Department, Designation, EmployeeProfile


class GlobalSearchService:
    @staticmethod
    def search(query, limit=6):
        if not query:
            return []
        return (
            GlobalSearchService._users(query, limit)
            + GlobalSearchService._employees(query, limit)
            + GlobalSearchService._departments(query, limit)
            + GlobalSearchService._designations(query, limit)
        )[: limit * 4]

    @staticmethod
    def _users(query, limit):
        User = get_user_model()
        return [
            {
                "type": "User",
                "title": user.full_name,
                "subtitle": user.email,
                "url": reverse("accounts:profile") if user else "#",
            }
            for user in User.objects.filter(full_name__icontains=query).order_by(
                "full_name"
            )[:limit]
        ]

    @staticmethod
    def _employees(query, limit):
        queryset = EmployeeProfile.objects.select_related("user").filter(
            user__full_name__icontains=query
        ) | EmployeeProfile.objects.select_related("user").filter(
            employee_id__icontains=query
        )
        return [
            {
                "type": "Employee",
                "title": employee.user.full_name,
                "subtitle": employee.employee_id,
                "url": reverse("employees:employee_detail", kwargs={"pk": employee.pk}),
            }
            for employee in queryset.order_by("user__full_name")[:limit]
        ]

    @staticmethod
    def _departments(query, limit):
        return [
            {
                "type": "Department",
                "title": department.name,
                "subtitle": "Department",
                "url": reverse(
                    "employees:department_detail", kwargs={"pk": department.pk}
                ),
            }
            for department in Department.objects.filter(name__icontains=query).order_by(
                "name"
            )[:limit]
        ]

    @staticmethod
    def _designations(query, limit):
        return [
            {
                "type": "Designation",
                "title": designation.title,
                "subtitle": f"Level {designation.level}",
                "url": reverse("employees:organization_chart"),
            }
            for designation in Designation.objects.filter(
                title__icontains=query
            ).order_by("level", "title")[:limit]
        ]
