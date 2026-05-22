from django.contrib import admin

from .models import (
    Activity,
    ApprovalInstance,
    ApprovalStage,
    ApprovalWorkflow,
    AuditLog,
)


class ApprovalStageInline(admin.TabularInline):
    model = ApprovalStage
    extra = 0


@admin.register(ApprovalWorkflow)
class ApprovalWorkflowAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at", "updated_at")
    search_fields = ("name", "description")
    list_filter = ("is_active",)
    inlines = [ApprovalStageInline]


@admin.register(ApprovalInstance)
class ApprovalInstanceAdmin(admin.ModelAdmin):
    list_display = ("workflow", "submitted_by", "current_stage", "status", "created_at")
    list_filter = ("status", "workflow")
    search_fields = ("workflow__name", "submitted_by__full_name", "submitted_by__email")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "model_name", "object_id", "user", "timestamp")
    list_filter = ("action", "model_name")
    search_fields = ("model_name", "object_id", "user__email", "user__full_name")
    readonly_fields = ("created_at", "updated_at", "timestamp")


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("actor", "verb", "target_type", "target_id", "timestamp")
    list_filter = ("target_type",)
    search_fields = ("actor__full_name", "verb", "target_type", "target_id")
    readonly_fields = ("created_at", "updated_at", "timestamp")
