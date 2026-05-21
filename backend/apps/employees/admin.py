from django.contrib import admin

from .models import Department, EmployeeProfile


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
