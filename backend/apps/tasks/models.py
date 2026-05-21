from apps.core.models import TimeStampedUUIDModel


class TaskBaseModel(TimeStampedUUIDModel):
    class Meta:
        abstract = True
