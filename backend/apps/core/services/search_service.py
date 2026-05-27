from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.employees.models import Department, Designation, EmployeeProfile
from apps.projects.models import Milestone, Project, Team


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
            + GlobalSearchService._teams(query, limit)
            + GlobalSearchService._projects(query, limit)
            + GlobalSearchService._milestones(query, limit)
        )[: limit * 7]

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

    @staticmethod
    def _teams(query, limit):
        return [
            {
                "type": "Team",
                "title": team.name,
                "subtitle": team.department.name,
                "url": reverse("projects:team_detail", kwargs={"pk": team.pk}),
            }
            for team in Team.objects.select_related("department")
            .filter(name__icontains=query)
            .order_by("name")[:limit]
        ]

    @staticmethod
    def _projects(query, limit):
        queryset = Project.objects.filter(
            name__icontains=query
        ) | Project.objects.filter(code__icontains=query)
        return [
            {
                "type": "Project",
                "title": project.name,
                "subtitle": project.code,
                "url": reverse("projects:project_detail", kwargs={"pk": project.pk}),
            }
            for project in queryset.filter(is_archived=False).order_by("name")[:limit]
        ]

    @staticmethod
    def _milestones(query, limit):
        return [
            {
                "type": "Milestone",
                "title": milestone.name,
                "subtitle": milestone.project.code,
                "url": reverse(
                    "projects:project_detail", kwargs={"pk": milestone.project.pk}
                ),
            }
            for milestone in Milestone.objects.select_related("project")
            .filter(name__icontains=query)
            .order_by("due_date")[:limit]
        ]
