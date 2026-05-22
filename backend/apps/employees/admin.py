from django.contrib import admin

from .models import (
    Department,
    Designation,
    EmployeeHierarchy,
    EmployeeProfile,
    OrganizationPosition,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "head", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description", "head__full_name", "head__email")
    readonly_fields = ("created_at", "updated_at")


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = (
        "employee_id",
        "user",
        "designation",
        "department",
        "manager",
        "employment_status",
    )
    list_filter = ("employment_status", "department")
    search_fields = ("employee_id", "user__full_name", "user__email", "designation")
    readonly_fields = ("created_at", "updated_at")


@admin.register(EmployeeHierarchy)
class EmployeeHierarchyAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "reporting_manager",
        "effective_from",
        "effective_to",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("employee__user__full_name", "reporting_manager__user__full_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ("title", "level", "created_at", "updated_at")
    search_fields = ("title",)
    list_filter = ("level",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(OrganizationPosition)
class OrganizationPositionAdmin(admin.ModelAdmin):
    list_display = ("employee", "designation", "department", "reporting_position")
    list_filter = ("department", "designation")
    search_fields = (
        "employee__user__full_name",
        "designation__title",
        "department__name",
    )
    readonly_fields = ("created_at", "updated_at")
