import csv
import io
from datetime import date, datetime, timedelta

from django.db.models import Avg, Count, F, Q, Sum
from django.utils import timezone

from apps.attendance.models import Attendance, LeaveRequest
from apps.employees.models import Department, EmployeeProfile
from apps.projects.models import Milestone, Project, ProjectMember
from apps.tasks.models import Task


class AnalyticsSelector:
    """Read-only queries for analytics data."""

    # ── Employee Stats ──────────────────────────────────────

    @staticmethod
    def employee_counts():
        return {
            "total": EmployeeProfile.objects.filter(user__is_active=True).count(),
            "by_department": dict(
                EmployeeProfile.objects.filter(user__is_active=True)
                .values("department__name")
                .annotate(count=Count("id"))
                .values_list("department__name", "count")
            ),
            "by_designation": dict(
                EmployeeProfile.objects.filter(user__is_active=True)
                .values("designation")
                .annotate(count=Count("id"))
                .values_list("designation", "count")
            ),
            "new_this_month": EmployeeProfile.objects.filter(
                user__is_active=True, created_at__gte=timezone.now() - timedelta(days=30)
            ).count(),
        }

    @staticmethod
    def employee_performance(employee_id=None, department_id=None, date_from=None, date_to=None):
        q = Q(user__is_active=True)
        if employee_id:
            q &= Q(id=employee_id)
        if department_id:
            q &= Q(department_id=department_id)
        employees = EmployeeProfile.objects.filter(q)
        return employees

    # ── Project Stats ───────────────────────────────────────

    @staticmethod
    def project_stats():
        total = Project.objects.count()
        active = Project.objects.filter(status="active").count()
        completed = Project.objects.filter(status="completed").count()
        on_hold = Project.objects.filter(status="on_hold").count()
        at_risk = Project.objects.filter(status="at_risk").count()
        return {
            "total": total,
            "active": active,
            "completed": completed,
            "on_hold": on_hold,
            "at_risk": at_risk,
            "completion_rate": round(completed / total * 100, 1) if total else 0,
            "by_department": dict(
                Project.objects.values("department__name")
                .annotate(count=Count("id"))
                .values_list("department__name", "count")
            ),
        }

    @staticmethod
    def projects_by_status():
        return dict(
            Project.objects.values("status")
            .annotate(count=Count("id"))
            .values_list("status", "count")
        )

    @staticmethod
    def project_progress(project_id=None):
        q = Q()
        if project_id:
            q &= Q(id=project_id)
        projects = Project.objects.filter(q).annotate(
            task_count=Count("tasks", distinct=True),
            completed_tasks=Count("tasks", filter=Q(tasks__status="done"), distinct=True),
            overdue_tasks=Count(
                "tasks",
                filter=Q(tasks__due_date__lt=timezone.now()) & ~Q(tasks__status="done"),
                distinct=True,
            ),
        )
        result = []
        for p in projects:
            result.append(
                {
                    "id": p.id,
                    "name": p.name,
                    "status": p.status,
                    "task_count": p.task_count,
                    "completed_tasks": p.completed_tasks,
                    "overdue_tasks": p.overdue_tasks,
                    "progress": round(p.completed_tasks / p.task_count * 100, 1) if p.task_count else 0,
                }
            )
        return result

    # ── Task Stats ──────────────────────────────────────────

    @staticmethod
    def task_stats(filters=None):
        q = Q()
        if filters:
            if filters.get("project_id"):
                q &= Q(project_id=filters["project_id"])
            if filters.get("assigned_to_id"):
                q &= Q(assignments__employee_id=filters["assigned_to_id"])
            if filters.get("status"):
                q &= Q(status=filters["status"])
            if filters.get("priority"):
                q &= Q(priority=filters["priority"])
            if filters.get("date_from"):
                q &= Q(created_at__gte=filters["date_from"])
            if filters.get("date_to"):
                q &= Q(created_at__lte=filters["date_to"])

        total = Task.objects.filter(q).count()
        return {
            "total": total,
            "todo": Task.objects.filter(q, status="todo").count(),
            "in_progress": Task.objects.filter(q, status="in_progress").count(),
            "done": Task.objects.filter(q, status="done").count(),
            "review": Task.objects.filter(q, status="review").count(),
            "blocked": Task.objects.filter(q, status="blocked").count(),
            "overdue": Task.objects.filter(q, due_date__lt=timezone.now()).exclude(status="done").count(),
            "completion_rate": round(
                Task.objects.filter(q, status="done").count() / total * 100, 1
            )
            if total
            else 0,
        }

    @staticmethod
    def tasks_by_priority():
        return dict(
            Task.objects.values("priority")
            .annotate(count=Count("id"))
            .values_list("priority", "count")
        )

    @staticmethod
    def tasks_by_assignee(project_id=None):
        q = Q()
        if project_id:
            q &= Q(task__project_id=project_id)
        return list(
            TaskAssignment.objects.filter(q)
            .values("employee__user__full_name", "employee_id")
            .annotate(count=Count("task", distinct=True))
            .order_by("-count")
        )

    @staticmethod
    def completion_trends(days=30):
        since = timezone.now() - timedelta(days=days)
        return list(
            Task.objects.filter(completed_at__gte=since)
            .extra({"date": "date(completed_at)"})
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

    @staticmethod
    def overdue_tasks(filters=None):
        q = Q(due_date__lt=timezone.now()) & ~Q(status="done")
        if filters:
            if filters.get("project_id"):
                q &= Q(project_id=filters["project_id"])
            if filters.get("assigned_to_id"):
                q &= Q(assignments__employee_id=filters["assigned_to_id"])
            if filters.get("department_id"):
                q &= Q(project__department_id=filters["department_id"])
        return Task.objects.filter(q).prefetch_related("assignments__employee__user", "project")

    @staticmethod
    def bottleneck_tasks():
        """Tasks blocked or stuck in review for > 3 days."""
        cutoff = timezone.now() - timedelta(days=3)
        return Task.objects.filter(
            Q(status="blocked") | (Q(status="review") & Q(updated_at__lt=cutoff)),
        ).prefetch_related("assignments__employee__user", "project")

    @staticmethod
    def workload_distribution(department_id=None):
        q = Q(user__is_active=True)
        if department_id:
            q &= Q(department_id=department_id)
        employees = EmployeeProfile.objects.filter(q)
        data = []
        for emp in employees:
            active_tasks = Task.objects.filter(
                assignments__employee=emp, status__in=["todo", "in_progress", "review"]
            ).distinct().count()
            overdue = (
                Task.objects.filter(
                    assignments__employee=emp, due_date__lt=timezone.now()
                )
                .exclude(status="done")
                .count()
            )
            data.append(
                {
                    "employee_id": emp.id,
                    "name": str(emp),
                    "department": emp.department.name if emp.department else "N/A",
                    "active_tasks": active_tasks,
                    "overdue_tasks": overdue,
                    "load_score": active_tasks + overdue * 2,
                }
            )
        return sorted(data, key=lambda x: x["load_score"], reverse=True)

    # ── Attendance Stats ────────────────────────────────────

    @staticmethod
    def attendance_stats(department_id=None, date_from=None, date_to=None):
        q = Q()
        if date_from:
            q &= Q(date__gte=date_from)
        if date_to:
            q &= Q(date__lte=date_to)
        if department_id:
            q &= Q(employee__department_id=department_id)

        total = Attendance.objects.filter(q).count()
        present = Attendance.objects.filter(q, status="present").count()
        absent = Attendance.objects.filter(q, status="absent").count()
        late = Attendance.objects.filter(q, status="late").count()
        half_day = Attendance.objects.filter(q, status="half_day").count()

        pending_leaves = LeaveRequest.objects.filter(status="pending").count()
        approved_leaves = LeaveRequest.objects.filter(status="approved").count()

        return {
            "total_records": total,
            "present": present,
            "absent": absent,
            "late": late,
            "half_day": half_day,
            "attendance_rate": round(present / total * 100, 1) if total else 0,
            "pending_leaves": pending_leaves,
            "approved_leaves": approved_leaves,
        }

    @staticmethod
    def monthly_attendance_trend(months=6):
        since = timezone.now() - timedelta(days=months * 30)
        return list(
            Attendance.objects.filter(date__gte=since)
            .extra({"month": "strftime('%%Y-%%m', date)"})
            .values("month")
            .annotate(
                present=Count("id", filter=Q(status="present")),
                absent=Count("id", filter=Q(status="absent")),
            )
            .order_by("month")
        )

    # ── Milestone Stats ─────────────────────────────────────

    @staticmethod
    def milestone_stats(project_id=None):
        q = Q()
        if project_id:
            q &= Q(project_id=project_id)
        total = Milestone.objects.filter(q).count()
        completed = Milestone.objects.filter(q, status="completed").count()
        overdue = Milestone.objects.filter(q, due_date__lt=timezone.now()).exclude(status="completed").count()
        return {
            "total": total,
            "completed": completed,
            "overdue": overdue,
            "completion_rate": round(completed / total * 100, 1) if total else 0,
        }

    @staticmethod
    def sla_breaches(days=30):
        """Tasks that exceeded their estimated hours by > 20%."""
        since = timezone.now() - timedelta(days=days)
        return Task.objects.filter(
            completed_at__gte=since,
            estimated_hours__gt=0,
        ).extra(
            where=["EXTRACT(EPOCH FROM (completed_at - created_at))/3600 > estimated_hours * 1.2"]
        ).prefetch_related("assignments__employee__user", "project")
