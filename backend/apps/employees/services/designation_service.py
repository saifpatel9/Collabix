from django.db import transaction
from django.db.models import Q

from ..models import Designation


class DesignationService:
    @staticmethod
    def all_designations():
        return Designation.objects.order_by("level", "title")

    @staticmethod
    def search(queryset, search_term):
        if search_term:
            queryset = queryset.filter(
                Q(title__icontains=search_term)
                | Q(description__icontains=search_term)
            )
        return queryset

    @staticmethod
    @transaction.atomic
    def create(*, cleaned_data):
        return Designation.objects.create(**cleaned_data)

    @staticmethod
    @transaction.atomic
    def update(*, designation, cleaned_data):
        for field, value in cleaned_data.items():
            setattr(designation, field, value)
        designation.save()
        return designation

    @staticmethod
    @transaction.atomic
    def delete(*, designation):
        designation.delete()
