import uuid

from django.conf import settings
from django.db import models


class TimeStampedUUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModel(TimeStampedUUIDModel):
    class Meta:
        abstract = True


class SoftDeleteModel(BaseModel):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True


class ApprovalWorkflow(BaseModel):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "approval_workflows"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class ApprovalStage(BaseModel):
    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.CASCADE,
        related_name="stages",
    )
    stage_number = models.PositiveIntegerField()
    approver_role = models.CharField(max_length=50, blank=True)
    approver_designation = models.ForeignKey(
        "employees.Designation",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="approval_stages",
    )
    auto_escalation_days = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "approval_stages"
        ordering = ["workflow", "stage_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["workflow", "stage_number"],
                name="uniq_workflow_stage_number",
            )
        ]

    def __str__(self) -> str:
        return f"{self.workflow.name} - Stage {self.stage_number}"


class ApprovalInstance(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.PROTECT,
        related_name="instances",
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="approval_instances",
    )
    current_stage = models.ForeignKey(
        ApprovalStage,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="current_instances",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    class Meta:
        db_table = "approval_instances"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["status"], name="approval_instance_status_idx")]

    def __str__(self) -> str:
        return f"{self.workflow.name} - {self.get_status_display()}"


class AuditLog(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50)
    model_name = models.CharField(max_length=150)
    object_id = models.CharField(max_length=64)
    old_data = models.JSONField(blank=True, null=True)
    new_data = models.JSONField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["model_name", "object_id"], name="audit_object_idx"),
            models.Index(fields=["action"], name="audit_action_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.action} {self.model_name}:{self.object_id}"


class Activity(BaseModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="activities",
    )
    verb = models.CharField(max_length=255)
    target_type = models.CharField(max_length=150)
    target_id = models.CharField(max_length=64)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "activities"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(
                fields=["target_type", "target_id"], name="activity_target_idx"
            ),
            models.Index(fields=["timestamp"], name="activity_timestamp_idx"),
        ]

    def __str__(self) -> str:
        actor = self.actor.full_name if self.actor else "System"
        return f"{actor} {self.verb}"
