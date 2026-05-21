from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q

from apps.accounts.models import User

from ..models import EmployeeProfile


class EmployeeService:
    @staticmethod
    def visible_to(user):
        queryset = EmployeeProfile.objects.select_related(
            "user", "department", "manager__user"
        )
        if user.is_superuser or user.role == User.Role.ADMIN:
            return queryset
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
        if employment_status:
            queryset = queryset.filter(employment_status=employment_status)
        return queryset

    @staticmethod
    @transaction.atomic
    def create(*, cleaned_data):
        user_data = EmployeeService._extract_user_data(cleaned_data)
        UserModel = get_user_model()
        user = UserModel.objects.create_user(
            email=user_data["email"],
            password=None,
            full_name=user_data["full_name"],
            role=user_data["role"],
            phone=user_data["phone"],
            is_active=True,
        )
        return EmployeeProfile.objects.create(user=user, **cleaned_data)

    @staticmethod
    @transaction.atomic
    def update(*, employee, cleaned_data):
        user_data = EmployeeService._extract_user_data(cleaned_data)
        for field, value in user_data.items():
            setattr(employee.user, field, value)
        employee.user.save(
            update_fields=["full_name", "email", "role", "phone", "updated_at"]
        )

        for field, value in cleaned_data.items():
            setattr(employee, field, value)
        employee.save()
        return employee

    @staticmethod
    @transaction.atomic
    def update_status(*, employee, status):
        employee.employment_status = status
        employee.save(update_fields=["employment_status", "updated_at"])
        return employee

    @staticmethod
    def _extract_user_data(cleaned_data):
        return {
            "full_name": cleaned_data.pop("user_full_name"),
            "email": cleaned_data.pop("user_email"),
            "role": cleaned_data.pop("user_role"),
            "phone": cleaned_data.pop("user_phone", ""),
        }
