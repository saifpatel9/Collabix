from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q, CheckConstraint
from django.utils import timezone

from apps.core.models import BaseModel


def task_attachment_upload_path(instance, filename):
    # Fallback for unsaved tasks
    if instance.task_id:
        return f"uploads/tasks/{instance.task_id}/{filename}"
    return f"uploads/tasks/temp/{filename}"


class TaskBaseModel(BaseModel):
    class Meta:
        abstract = True


class Task(TaskBaseModel):
    class Status(models.TextChoices):
        BACKLOG = "backlog", "Backlog"
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        REVIEW = "review", "Review"
        BLOCKED = "blocked", "Blocked"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    project = models.ForeignKey(
        "projects.Project", on_delete=models.CASCADE, related_name="tasks"
    )
    milestone = models.ForeignKey(
        "projects.Milestone",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="tasks",
    )
    title = models.CharField(max_length=220)
    description = models.TextField(blank=True)
    task_code = models.CharField(max_length=60, unique=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.BACKLOG
    )
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )
    estimated_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    actual_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(
        "employees.EmployeeProfile",
        on_delete=models.PROTECT,
        related_name="created_tasks",
    )
    updated_by = models.ForeignKey(
        "employees.EmployeeProfile",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="updated_tasks",
    )
    is_archived = models.BooleanField(default=False)

    class Meta:
        db_table = "tasks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project", "status"], name="task_project_status_idx"),
            models.Index(fields=["milestone", "status"], name="task_mstone_status_idx"),
            models.Index(fields=["priority"], name="task_priority_idx"),
            models.Index(fields=["due_date"], name="task_due_date_idx"),
            models.Index(fields=["created_by"], name="task_created_by_idx"),
            models.Index(fields=["is_archived"], name="task_archived_idx"),
            models.Index(fields=["task_code"], name="task_code_idx"),
        ]

    def clean(self):
        if self.milestone_id and self.project_id:
            if self.milestone.project_id != self.project_id:
                raise ValidationError("Milestone must belong to the selected project.")
        if self.start_date and self.due_date and self.start_date > self.due_date:
            raise ValidationError("Start date cannot be after due date.")
        if self.status == self.Status.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        if self.status != self.Status.COMPLETED:
            self.completed_at = None

    @property
    def assignees(self):
        return self.assignments.select_related("employee__user").order_by(
            "employee__user__full_name", "-assigned_at"
        )

    @property
    def checklist_progress(self):
        total = TaskChecklistItem.objects.filter(checklist__task=self).count()
        completed = TaskChecklistItem.objects.filter(
            checklist__task=self, is_completed=True
        ).count()
        return {
            "total": total,
            "completed": completed,
            "percentage": round((completed / total) * 100) if total else 0,
        }

    def __str__(self):
        return f"{self.task_code} - {self.title}"


class TaskAssignment(TaskBaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="assignments")
    employee = models.ForeignKey(
        "employees.EmployeeProfile",
        on_delete=models.CASCADE,
        related_name="task_assignments",
    )
    assigned_by = models.ForeignKey(
        "employees.EmployeeProfile",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="task_assignments_made",
    )
    assigned_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "task_assignments"
        ordering = ["-assigned_at"]
        indexes = [
            models.Index(fields=["task", "employee"], name="task_assign_employee_idx"),
            models.Index(fields=["employee"], name="task_assign_emp_idx"),
            models.Index(fields=["assigned_at"], name="task_assign_at_idx"),
        ]

    def __str__(self):
        return f"{self.employee} -> {self.task}"


class TaskComment(TaskBaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        "employees.EmployeeProfile",
        on_delete=models.PROTECT,
        related_name="task_comments",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="replies",
    )
    comment = models.TextField()

    class Meta:
        db_table = "task_comments"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["task", "created_at"], name="task_comment_time_idx"),
            models.Index(fields=["author"], name="task_comment_author_idx"),
            models.Index(fields=["parent"], name="task_comment_parent_idx"),
        ]

    def __str__(self):
        return f"Comment on {self.task}"


class TaskAttachment(TaskBaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments")
    uploaded_by = models.ForeignKey(
        "employees.EmployeeProfile",
        on_delete=models.PROTECT,
        related_name="task_attachments",
    )
    file = models.FileField(upload_to=task_attachment_upload_path)
    original_filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "task_attachments"
        ordering = ["-uploaded_at"]
        indexes = [
            models.Index(fields=["task", "uploaded_at"], name="task_attach_time_idx"),
            models.Index(fields=["uploaded_by"], name="task_attach_user_idx"),
        ]

    def __str__(self):
        return self.original_filename


class TaskActivity(TaskBaseModel):
    class Type(models.TextChoices):
        CREATED = "created", "Created"
        STATUS_CHANGED = "status_changed", "Status Changed"
        ASSIGNED = "assigned", "Assigned"
        PRIORITY_CHANGED = "priority_changed", "Priority Changed"
        DUE_DATE_CHANGED = "due_date_changed", "Due Date Changed"
        COMMENTED = "commented", "Commented"
        ATTACHED = "attached", "Attached"
        CHECKLIST_UPDATED = "checklist_updated", "Checklist Updated"
        DEPENDENCY_UPDATED = "dependency_updated", "Dependency Updated"
        ARCHIVED = "archived", "Archived"
        DELETED = "deleted", "Deleted"
        UPDATED = "updated", "Updated"

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="activities")
    actor = models.ForeignKey(
        "employees.EmployeeProfile",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="task_activities",
    )
    activity_type = models.CharField(max_length=40, choices=Type.choices)
    message = models.CharField(max_length=255)
    old_value = models.JSONField(blank=True, null=True)
    new_value = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = "task_activities"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["task", "created_at"], name="task_activity_time_idx"),
            models.Index(fields=["activity_type"], name="task_activity_type_idx"),
            models.Index(fields=["actor"], name="task_activity_actor_idx"),
        ]

    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.task}"


class TaskChecklist(TaskBaseModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="checklists")
    title = models.CharField(max_length=180)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "task_checklists"
        ordering = ["position", "created_at"]
        indexes = [models.Index(fields=["task", "position"], name="task_cl_pos_idx")]

    @property
    def progress(self):
        total = self.items.count()
        completed = self.items.filter(is_completed=True).count()
        return {
            "total": total,
            "completed": completed,
            "percentage": round((completed / total) * 100) if total else 0,
        }

    def __str__(self):
        return self.title


class TaskChecklistItem(TaskBaseModel):
    checklist = models.ForeignKey(
        TaskChecklist, on_delete=models.CASCADE, related_name="items"
    )
    title = models.CharField(max_length=220)
    is_completed = models.BooleanField(default=False)
    completed_by = models.ForeignKey(
        "employees.EmployeeProfile",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="completed_task_checklist_items",
    )
    completed_at = models.DateTimeField(blank=True, null=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "task_checklist_items"
        ordering = ["position", "created_at"]
        indexes = [
            models.Index(fields=["checklist", "position"], name="task_cli_pos_idx"),
            models.Index(fields=["is_completed"], name="task_cli_completed_idx"),
        ]

    def clean(self):
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        if not self.is_completed:
            self.completed_at = None
            self.completed_by = None

    def __str__(self):
        return self.title


class TaskDependency(TaskBaseModel):
    class Type(models.TextChoices):
        FINISH_TO_START = "finish_to_start", "Finish to Start"
        START_TO_START = "start_to_start", "Start to Start"
        FINISH_TO_FINISH = "finish_to_finish", "Finish to Finish"

    predecessor_task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="successor_dependencies"
    )
    successor_task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="predecessor_dependencies"
    )
    dependency_type = models.CharField(
        max_length=30, choices=Type.choices, default=Type.FINISH_TO_START
    )

    class Meta:
        db_table = "task_dependencies"
        ordering = ["created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["predecessor_task", "successor_task", "dependency_type"],
                name="uniq_task_dependency",
            ),
            CheckConstraint(
                condition=~Q(predecessor_task=models.F("successor_task")),  # FIXED
                name="prevent_task_self_dependency",
            ),
        ]
        indexes = [
            models.Index(fields=["predecessor_task"], name="task_dep_predecessor_idx"),
            models.Index(fields=["successor_task"], name="task_dep_successor_idx"),
        ]

    def clean(self):
        if self.predecessor_task_id == self.successor_task_id:
            raise ValidationError("A task cannot depend on itself.")
        if self.predecessor_task_id and self.successor_task_id:
            if self._creates_cycle(self.predecessor_task_id, self.successor_task_id):
                raise ValidationError("Circular task dependencies are not allowed.")

    def _creates_cycle(self, predecessor_id, successor_id):
        visited = set()
        stack = [predecessor_id]
        while stack:
            current = stack.pop()
            if current == successor_id:
                return True
            if current in visited:
                continue
            visited.add(current)
            stack.extend(
                TaskDependency.objects.filter(successor_task_id=current)
                .exclude(pk=self.pk)
                .values_list("predecessor_task_id", flat=True)
            )
        return False

    def __str__(self):
        return f"{self.predecessor_task} -> {self.successor_task}"