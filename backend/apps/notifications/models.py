from apps.core.models import TimeStampedUUIDModel


class NotificationBaseModel(TimeStampedUUIDModel):
    class Meta:
        abstract = True
