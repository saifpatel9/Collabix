from apps.core.models import TimeStampedUUIDModel


class AttendanceBaseModel(TimeStampedUUIDModel):
    class Meta:
        abstract = True
