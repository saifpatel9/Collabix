from apps.core.models import TimeStampedUUIDModel


class EmployeeBaseModel(TimeStampedUUIDModel):
    class Meta:
        abstract = True
