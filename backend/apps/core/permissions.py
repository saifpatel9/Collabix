from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from apps.accounts.models import User


def user_has_role(user, roles: tuple[str, ...]) -> bool:
    return bool(
        user and user.is_authenticated and (user.is_superuser or user.role in roles)
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
    allowed_roles = (User.Role.ADMIN,)


class ManagerRequiredMixin(RoleRequiredMixin):
    allowed_roles = (
        User.Role.ADMIN,
        User.Role.DEPARTMENT_ADMIN,
        User.Role.HR_MANAGER,
        User.Role.PROJECT_MANAGER,
        User.Role.MANAGER,
    )


class HRManagerRequiredMixin(RoleRequiredMixin):
    allowed_roles = (User.Role.ADMIN, User.Role.HR_MANAGER)


class DepartmentAdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = (User.Role.ADMIN, User.Role.DEPARTMENT_ADMIN, User.Role.HR_MANAGER)


class ProjectManagerRequiredMixin(RoleRequiredMixin):
    allowed_roles = (User.Role.ADMIN, User.Role.PROJECT_MANAGER, User.Role.MANAGER)


class EmployeeRequiredMixin(RoleRequiredMixin):
    allowed_roles = (
        User.Role.ADMIN,
        User.Role.DEPARTMENT_ADMIN,
        User.Role.HR_MANAGER,
        User.Role.PROJECT_MANAGER,
        User.Role.MANAGER,
        User.Role.EMPLOYEE,
    )


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
        user = self.request.user
        if user.is_superuser or user.role == User.Role.ADMIN:
            return True
        if user.role == User.Role.MANAGER:
            return employee.manager and employee.manager.user_id == user.id
        return employee.user_id == user.id

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        self.employee_object = self.get_employee_object()
        if not self.can_access_employee(self.employee_object):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
