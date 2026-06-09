from rest_framework.permissions import BasePermission

from apps.core.rbac.permissions import can_manage_employees, can_view_employee_directory


class CanViewEmployeeDirectory(BasePermission):
    def has_permission(self, request, view):
        return can_view_employee_directory(request.user)


class CanManageEmployees(BasePermission):
    def has_permission(self, request, view):
        return can_manage_employees(request.user)
