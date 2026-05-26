from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import BaseModel


class ProjectBaseModel(BaseModel):
    class Meta:
        abstract = True


class Team(ProjectBaseModel):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    team_lead = models.ForeignKey(
        "employees.EmployeeProfile",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="led_teams",
    )
    department = models.ForeignKey(
        "employees.Department",
        on_delete=models.PROTECT,
        related_name="teams",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "teams"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"], name="team_name_idx"),
            models.Index(
                fields=["department", "is_active"], name="team_dept_active_idx"
            ),
        ]

    def __str__(self) -> str:
        return self.name


class TeamMembership(ProjectBaseModel):
    class Role(models.TextChoices):
        TEAM_LEAD = "team_lead", "Team Lead"
        SENIOR_MEMBER = "senior_member", "Senior Member"
        MEMBER = "member", "Member"

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="memberships")
    employee = models.ForeignKey(
        "employees.EmployeeProfile",
        on_delete=models.CASCADE,
        related_name="team_memberships",
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "team_memberships"
        ordering = ["team__name", "employee__user__full_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["team", "employee"], name="uniq_team_employee_membership"
            )
        ]
        indexes = [
            models.Index(fields=["team", "role"], name="team_member_role_idx"),
            models.Index(fields=["employee"], name="team_member_employee_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.employee} - {self.team}"


class Project(ProjectBaseModel):
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        PLANNING = "planning", "Planning"
        ACTIVE = "active", "Active"
        ON_HOLD = "on_hold", "On Hold"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    name = models.CharField(max_length=180)
    code = models.CharField(max_length=40, unique=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        "employees.EmployeeProfile",
        on_delete=models.PROTECT,
        related_name="owned_projects",
    )
    department = models.ForeignKey(
        "employees.Department",
        on_delete=models.PROTECT,
        related_name="projects",
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="projects",
    )
    start_date = models.DateField(blank=True, null=True)
    target_end_date = models.DateField(blank=True, null=True)
    actual_end_date = models.DateField(blank=True, null=True)
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PLANNING
    )
    budget = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    is_archived = models.BooleanField(default=False)

    class Meta:
        db_table = "projects"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code"], name="project_code_idx"),
            models.Index(fields=["status"], name="project_status_idx"),
            models.Index(
                fields=["department", "status"], name="project_dept_status_idx"
            ),
            models.Index(fields=["is_archived"], name="project_archived_idx"),
        ]

    def clean(self):
        if (
            self.start_date
            and self.target_end_date
            and self.start_date > self.target_end_date
        ):
            raise ValidationError("Start date cannot be after target end date.")
        if (
            self.actual_end_date
            and self.start_date
            and self.actual_end_date < self.start_date
        ):
            raise ValidationError("Actual end date cannot be before start date.")

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class ProjectMember(ProjectBaseModel):
    class Role(models.TextChoices):
        PROJECT_MANAGER = "project_manager", "Project Manager"
        TEAM_LEAD = "team_lead", "Team Lead"
        CONTRIBUTOR = "contributor", "Contributor"
        VIEWER = "viewer", "Viewer"

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="memberships"
    )
    employee = models.ForeignKey(
        "employees.EmployeeProfile",
        on_delete=models.CASCADE,
        related_name="project_memberships",
    )
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.CONTRIBUTOR
    )

    class Meta:
        db_table = "project_members"
        ordering = ["project__name", "employee__user__full_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "employee"], name="uniq_project_employee_member"
            )
        ]
        indexes = [
            models.Index(fields=["project", "role"], name="project_member_role_idx"),
            models.Index(fields=["employee"], name="project_member_employee_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.employee} - {self.project}"


class Milestone(ProjectBaseModel):
    class Status(models.TextChoices):
        NOT_STARTED = "not_started", "Not Started"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        DELAYED = "delayed", "Delayed"

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="milestones"
    )
    name = models.CharField(max_length=180)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.NOT_STARTED
    )

    class Meta:
        db_table = "milestones"
        ordering = ["due_date", "name"]
        indexes = [
            models.Index(
                fields=["project", "status"], name="milestone_project_status_idx"
            ),
            models.Index(fields=["due_date"], name="milestone_due_date_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.project.code} - {self.name}"
