from django.contrib import admin

from .models import (
    Task,
    TaskActivity,
    TaskAssignment,
    TaskAttachment,
    TaskChecklist,
    TaskChecklistItem,
    TaskComment,
    TaskDependency,
)


class TaskAssignmentInline(admin.TabularInline):
    model = TaskAssignment
    extra = 0
    autocomplete_fields = ("employee", "assigned_by")


class TaskChecklistInline(admin.TabularInline):
    model = TaskChecklist
    extra = 0


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "task_code",
        "title",
        "project",
        "status",
        "priority",
        "due_date",
        "is_archived",
    )
    list_filter = ("status", "priority", "is_archived", "project")
    search_fields = ("task_code", "title", "description", "project__name")
    autocomplete_fields = ("project", "milestone", "created_by", "updated_by")
    inlines = (TaskAssignmentInline, TaskChecklistInline)


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ("task", "author", "created_at")
    search_fields = ("task__task_code", "comment", "author__user__full_name")
    autocomplete_fields = ("task", "author", "parent")


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ("task", "original_filename", "uploaded_by", "uploaded_at")
    autocomplete_fields = ("task", "uploaded_by")


@admin.register(TaskActivity)
class TaskActivityAdmin(admin.ModelAdmin):
    list_display = ("task", "activity_type", "actor", "created_at")
    list_filter = ("activity_type",)
    autocomplete_fields = ("task", "actor")


@admin.register(TaskChecklist)
class TaskChecklistAdmin(admin.ModelAdmin):
    list_display = ("task", "title", "position")
    search_fields = ("title", "task__task_code", "task__title")
    autocomplete_fields = ("task",)


@admin.register(TaskChecklistItem)
class TaskChecklistItemAdmin(admin.ModelAdmin):
    list_display = ("checklist", "title", "is_completed", "position")
    autocomplete_fields = ("checklist", "completed_by")


@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    list_display = ("predecessor_task", "successor_task", "dependency_type")
    list_filter = ("dependency_type",)
    autocomplete_fields = ("predecessor_task", "successor_task")
