from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from apps.core.rbac.permissions import (
    ADMIN_ONLY_ROLES,
    ALL_MANAGEMENT_ROLES,
    DEPARTMENT_ACCESS_ROLES,
    HR_ACCESS_ROLES,
    INTERNAL_USER_ROLES,
    PROJECT_MODULE_ACCESS_ROLES,
    user_has_role,
)

from apps.core.rbac.rules import can_access_employee


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    allowed_roles: tuple[str, ...] = ()

    def test_func(self):
        return user_has_role(self.request.user, self.allowed_roles)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ADMIN_ONLY_ROLES


class ManagerRequiredMixin(RoleRequiredMixin):
    allowed_roles = ALL_MANAGEMENT_ROLES


class HRManagerRequiredMixin(RoleRequiredMixin):
    allowed_roles = HR_ACCESS_ROLES


class DepartmentAdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = DEPARTMENT_ACCESS_ROLES


class ProjectManagerRequiredMixin(RoleRequiredMixin):
    allowed_roles = PROJECT_MODULE_ACCESS_ROLES


class EmployeeRequiredMixin(RoleRequiredMixin):
    allowed_roles = INTERNAL_USER_ROLES


class EmployeeAccessMixin(LoginRequiredMixin):
    object_kwarg = "pk"

    def get_employee_object(self):
        from apps.employees.models import EmployeeProfile

        return get_object_or_404(
            EmployeeProfile.objects.select_related(
                "user",
                "department",
                "manager__user",
            ),
            pk=self.kwargs[self.object_kwarg],
        )

    def can_access_employee(self, employee):
        return can_access_employee(self.request.user, employee)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        self.employee_object = self.get_employee_object()

        if not self.can_access_employee(self.employee_object):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)