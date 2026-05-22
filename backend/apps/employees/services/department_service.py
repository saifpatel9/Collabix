from django.db import transaction
from django.db.models import Q

from apps.accounts.models import User

from ..models import Department


class DepartmentService:
    @staticmethod
    def visible_to(user):
        if (
            user.role
            in (
                User.Role.ADMIN,
                User.Role.DEPARTMENT_ADMIN,
                User.Role.HR_MANAGER,
                User.Role.PROJECT_MANAGER,
                User.Role.MANAGER,
            )
            or user.is_superuser
        ):
            return Department.objects.select_related("head").all()
        return Department.objects.none()

    @staticmethod
    def search(queryset, search_term):
        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term) | Q(description__icontains=search_term)
            )
        return queryset

    @staticmethod
    @transaction.atomic
    def create(*, cleaned_data):
        return Department.objects.create(**cleaned_data)

    @staticmethod
    @transaction.atomic
    def update(*, department, cleaned_data):
        for field, value in cleaned_data.items():
            setattr(department, field, value)
        department.save()
        return department

    @staticmethod
    @transaction.atomic
    def delete(*, department):
        department.delete()
