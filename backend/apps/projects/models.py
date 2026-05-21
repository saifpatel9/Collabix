from apps.core.models import TimeStampedUUIDModel


class ProjectBaseModel(TimeStampedUUIDModel):
    class Meta:
        abstract = True
