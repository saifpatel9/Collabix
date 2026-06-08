from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from apps.core.rbac import (
    ADMIN_ONLY_ROLES,
    ROLE_DEPARTMENT_ADMIN_REQUIRED,
    ROLE_EMPLOYEE_REQUIRED,
    ROLE_HR_MANAGER_REQUIRED,
    ROLE_MANAGER_REQUIRED,
    ROLE_PROJECT_MANAGER_REQUIRED,
    user_has_role,
    can_access_employee,
)


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
    allowed_roles = ROLE_MANAGER_REQUIRED


class HRManagerRequiredMixin(RoleRequiredMixin):
    allowed_roles = ROLE_HR_MANAGER_REQUIRED


class DepartmentAdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ROLE_DEPARTMENT_ADMIN_REQUIRED


class ProjectManagerRequiredMixin(RoleRequiredMixin):
    allowed_roles = ROLE_PROJECT_MANAGER_REQUIRED


class EmployeeRequiredMixin(RoleRequiredMixin):
    allowed_roles = ROLE_EMPLOYEE_REQUIRED


class EmployeeAccessMixin(LoginRequiredMixin):
    object_kwarg = "pk"

    def get_employee_object(self):
        from apps.employees.models import EmployeeProfile

        return get_object_or_404(
            EmployeeProfile.objects.select_related(
                "user", "department", "manager__user"
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
