from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Q

from apps.accounts.models import User
from apps.core.rbac.permissions import user_has_role
from apps.core.rbac.rules import can_access_employee
from apps.employees.tasks import employee_onboarding

from ..models import EmployeeProfile


class EmployeeService:
    @staticmethod
    def visible_to(user):
        queryset = EmployeeProfile.objects.select_related(
            "user", "department", "manager__user"
        )

        if user.is_superuser or user.role == User.Role.ADMIN:
            return queryset

        if user.role == User.Role.HR_MANAGER:
            return queryset

        if user.role == User.Role.DEPARTMENT_ADMIN:
            profile = getattr(user, "employee_profile", None)
            if not profile or not profile.department:
                return queryset.none()

            return queryset.filter(department=profile.department)

        if user.role == User.Role.MANAGER:
            return queryset.filter(Q(manager__user=user) | Q(user=user))

        return queryset.filter(user=user)

    @staticmethod
    def search_and_filter(
        queryset, *, search=None, department=None, manager=None, employment_status=None
    ):
        if search:
            queryset = queryset.filter(
                Q(user__full_name__icontains=search)
                | Q(user__email__icontains=search)
                | Q(employee_id__icontains=search)
            )

        if department:
            queryset = queryset.filter(department_id=department)

        if manager:
            queryset = queryset.filter(manager_id=manager)

        if not employment_status:
            employment_status = EmployeeProfile.EmploymentStatus.ACTIVE

        queryset = queryset.filter(employment_status=employment_status)

        return queryset
        
    @staticmethod
    @transaction.atomic
    def deactivate(*, employee, performed_by):
        if not user_has_role(performed_by, (User.Role.ADMIN, User.Role.HR_MANAGER)):
            raise PermissionDenied
        if employee.employment_status == EmployeeProfile.EmploymentStatus.INACTIVE:
            raise ValidationError("This employee is already inactive.")
        if employee.user.is_superuser:
            raise ValidationError("Cannot deactivate a superuser.")
        if performed_by == employee.user:
            raise ValidationError("You cannot deactivate yourself.")
            
        employee.employment_status = EmployeeProfile.EmploymentStatus.INACTIVE
        employee.user.is_active = False
        employee.save(update_fields=["employment_status", "updated_at"])
        employee.user.save(update_fields=["is_active", "updated_at"])
        
        return employee

    @staticmethod
    def _extract_user_data(cleaned_data):
        mapping = {
            "user_full_name": "full_name",
            "user_email": "email",
            "user_role": "role",
            "user_phone": "phone",
        }

        user_data = {}

        for serializer_field, user_field in mapping.items():
            if serializer_field in cleaned_data:
                user_data[user_field] = cleaned_data.pop(serializer_field)

        return user_data

    @staticmethod
    @transaction.atomic
    def create(*, cleaned_data, performed_by=None):
        if not user_has_role(
            performed_by,
            (User.Role.ADMIN, User.Role.HR_MANAGER)
        ):
            raise PermissionDenied

        user_data = EmployeeService._extract_user_data(cleaned_data)

        # Prevent non-admins from creating admin users
        requested_role = user_data.get("role")
        if (
            requested_role == User.Role.ADMIN
            and performed_by.role != User.Role.ADMIN
        ):
            raise PermissionDenied(
                "Only admins can assign the admin role."
            )

        UserModel = get_user_model()

        user = UserModel.objects.create_user(
        email=user_data["email"],
        password="ChangeMe@123",
        full_name=user_data["full_name"],
        role=user_data["role"],
        phone=user_data.get("phone", ""),
        is_active=True,
    )

        employee = EmployeeProfile.objects.create(
            user=user,
            **cleaned_data
        )
        employee_id = employee.id

        transaction.on_commit(
            lambda: employee_onboarding.delay(employee_id)
        )
        return employee

    @staticmethod
    @transaction.atomic
    def update(*, employee, cleaned_data, performed_by=None):
        if not can_access_employee(performed_by, employee):
            raise PermissionDenied

        user_data = EmployeeService._extract_user_data(cleaned_data)

        # Prevent non-admins from assigning the admin role
        requested_role = user_data.get("role")
        if (
            requested_role == User.Role.ADMIN
            and performed_by.role != User.Role.ADMIN
        ):
            raise PermissionDenied(
                "Only admins can assign the admin role."
            )

        for field, value in user_data.items():
            setattr(employee.user, field, value)

        employee.user.save(
            update_fields=["full_name", "email", "role", "phone"]
        )

        for field, value in cleaned_data.items():
            setattr(employee, field, value)

        employee.save()
        return employee