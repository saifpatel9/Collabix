import hashlib
import json
from datetime import timedelta

from django.core.cache import cache
from django.db.models import Avg, Count, F, Q, Sum
from django.utils import timezone

from apps.attendance.models import Attendance, LeaveRequest
from apps.employees.models import Department, EmployeeProfile
from apps.projects.models import Milestone, Project
from apps.reports.selectors.analytics_selector import AnalyticsSelector
from apps.tasks.models import Task


class AnalyticsService:
    CACHE_TTL = 300

    @staticmethod
    def _cache_key(prefix, user_id, **params):
        raw = f"{prefix}:{user_id}:" + json.dumps(params, sort_keys=True)
        return f"analytics:{hashlib.md5(raw.encode()).hexdigest()}"

    @staticmethod
    def _get_or_compute(key, ttl, compute_fn):
        result = cache.get(key)
        if result is not None:
            return result
        result = compute_fn()
        cache.set(key, result, ttl)
        return result

    @staticmethod
    def kpi_dashboard(user):
        key = AnalyticsService._cache_key("kpi_dashboard", user.id)
        return AnalyticsService._get_or_compute(key, AnalyticsService.CACHE_TTL, lambda: AnalyticsService._compute_kpi_dashboard(user))

    @staticmethod
    def _compute_kpi_dashboard(user):
        selector = AnalyticsSelector()
        employees = selector.employee_counts()
        projects = selector.project_stats()
        tasks = selector.task_stats()
        attendance = selector.attendance_stats(date_from=timezone.now().replace(day=1).date())
        task_stats = selector.task_stats()

        total_employees = EmployeeProfile.objects.filter(user__is_active=True).count()
        active_projects = Project.objects.filter(status="active").count()
        total_tasks = Task.objects.count()
        completed_tasks = Task.objects.filter(status="done").count()
        overdue_tasks = Task.objects.filter(due_date__lt=timezone.now()).exclude(status="done").count()
        attendance_total = Attendance.objects.filter(date=timezone.now().date()).count()
        attendance_present = Attendance.objects.filter(date=timezone.now().date(), status="present").count()
        attendance_rate = round(attendance_present / attendance_total * 100, 1) if attendance_total else 0
        productivity_score = round(completed_tasks / total_tasks * 100, 1) if total_tasks else 0
        team_performance = round(
            Task.objects.filter(status="done", completed_at__gte=timezone.now() - timedelta(days=30)).count()
            / max(Task.objects.filter(created_at__gte=timezone.now() - timedelta(days=30)).count(), 1) * 100, 1
        )

        return {
            "employees": employees,
            "projects": projects,
            "tasks": tasks,
            "attendance": attendance,
            "overdue_tasks_count": overdue_tasks,
            "pending_leaves": LeaveRequest.objects.filter(status="pending").count(),
            "active_milestones": Milestone.objects.exclude(status="completed").count(),
            "total_employees": total_employees,
            "active_projects": active_projects,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "overdue_tasks": overdue_tasks,
            "attendance_today": {"total": attendance_total, "present": attendance_present, "rate": attendance_rate},
            "productivity_score": productivity_score,
            "team_performance": team_performance,
        }

    @staticmethod
    def employee_performance(filters=None):
        key = AnalyticsService._cache_key("employee_performance", 0, **(filters or {}))
        return AnalyticsService._get_or_compute(key, AnalyticsService.CACHE_TTL, lambda: AnalyticsService._compute_employee_performance(filters))

    @staticmethod
    def _compute_employee_performance(filters=None):
        data = AnalyticsSelector.employee_performance(**filters) if filters else AnalyticsSelector.employee_performance()
        results = []
        for emp in data:
            total_tasks = Task.objects.filter(assignments__employee=emp).distinct().count()
            completed_tasks = Task.objects.filter(assignments__employee=emp, status="done").distinct().count()
            overdue_tasks = Task.objects.filter(assignments__employee=emp, due_date__lt=timezone.now()).exclude(status="done").distinct().count()
            attendance_today = Attendance.objects.filter(employee=emp, date=timezone.now().date()).first()
            results.append({
                "id": emp.id,
                "name": str(emp),
                "department": emp.department.name if emp.department else "N/A",
                "designation": emp.designation or "N/A",
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "overdue_tasks": overdue_tasks,
                "completion_rate": round(completed_tasks / total_tasks * 100, 1) if total_tasks else 0,
                "attendance_today": attendance_today.status if attendance_today else "N/A",
                "is_active": emp.user.is_active,
            })
        return sorted(results, key=lambda x: x["completion_rate"], reverse=True)

    @staticmethod
    def team_productivity(department_id=None, date_from=None, date_to=None):
        key = AnalyticsService._cache_key("team_productivity", 0, department_id=department_id or 0)
        return AnalyticsService._get_or_compute(key, AnalyticsService.CACHE_TTL, lambda: AnalyticsService._compute_team_productivity(department_id, date_from, date_to))

    @staticmethod
    def _compute_team_productivity(department_id=None, date_from=None, date_to=None):
        depts = Department.objects.filter(is_active=True)
        if department_id:
            depts = depts.filter(id=department_id)
        results = []
        for dept in depts:
            emp_ids = EmployeeProfile.objects.filter(department=dept, user__is_active=True).values_list("id", flat=True)
            total_tasks = Task.objects.filter(assignments__employee_id__in=emp_ids).distinct().count()
            completed = Task.objects.filter(assignments__employee_id__in=emp_ids, status="done").distinct().count()
            overdue = Task.objects.filter(assignments__employee_id__in=emp_ids, due_date__lt=timezone.now()).exclude(status="done").distinct().count()
            results.append({
                "department_id": dept.id,
                "department": dept.name,
                "employee_count": len(emp_ids),
                "total_tasks": total_tasks,
                "completed_tasks": completed,
                "overdue_tasks": overdue,
                "completion_rate": round(completed / total_tasks * 100, 1) if total_tasks else 0,
            })
        return sorted(results, key=lambda x: x["completion_rate"], reverse=True)

    @staticmethod
    def project_progress(project_id=None):
        key = AnalyticsService._cache_key("project_progress", 0, project_id=project_id or 0)
        return AnalyticsService._get_or_compute(key, AnalyticsService.CACHE_TTL, lambda: AnalyticsSelector.project_progress(project_id=project_id))

    @staticmethod
    def task_analytics(filters=None):
        key = AnalyticsService._cache_key("task_analytics", 0, **(filters or {}))
        return AnalyticsService._get_or_compute(key, AnalyticsService.CACHE_TTL, lambda: AnalyticsSelector.task_stats(filters=filters))

    @staticmethod
    def attendance_analytics(department_id=None, date_from=None, date_to=None):
        key = AnalyticsService._cache_key("attendance_analytics", 0, department_id=department_id or 0)
        return AnalyticsService._get_or_compute(key, AnalyticsService.CACHE_TTL, lambda: AnalyticsSelector.attendance_stats(department_id=department_id, date_from=date_from, date_to=date_to))

    @staticmethod
    def workflow_efficiency(date_from=None, date_to=None):
        q = Q()
        if date_from:
            q &= Q(created_at__gte=date_from)
        if date_to:
            q &= Q(created_at__lte=date_to)

        total_tasks = Task.objects.filter(q).count()
        completed_on_time = Task.objects.filter(q, status="done", due_date__gte=F("completed_at")).count()
        completed_late = Task.objects.filter(q, status="done", due_date__lt=F("completed_at")).count()
        overdue = Task.objects.filter(q, due_date__lt=timezone.now()).exclude(status="done").count()
        avg_completion_time = Task.objects.filter(q, status="done", completed_at__isnull=False).annotate(duration=F("completed_at") - F("created_at")).aggregate(avg=Avg("duration"))
        return {
            "total_tasks": total_tasks,
            "completed_on_time": completed_on_time,
            "completed_late": completed_late,
            "overdue": overdue,
            "on_time_rate": round(completed_on_time / total_tasks * 100, 1) if total_tasks else 0,
            "avg_completion_hours": round(avg_completion_time["avg"].total_seconds() / 3600, 1) if avg_completion_time.get("avg") else 0,
        }

    @staticmethod
    def workload_distribution(department_id=None):
        return AnalyticsSelector.workload_distribution(department_id=department_id)

    @staticmethod
    def completion_trends(days=30):
        return AnalyticsSelector.completion_trends(days=days)

    @staticmethod
    def sla_breaches(days=30):
        return AnalyticsSelector.sla_breaches(days=days)

    @staticmethod
    def bottleneck_analysis():
        return {
            "blocked_tasks": AnalyticsSelector.bottleneck_tasks(),
            "overdue_tasks": AnalyticsSelector.overdue_tasks(),
            "workload": AnalyticsSelector.workload_distribution()[:10],
        }
