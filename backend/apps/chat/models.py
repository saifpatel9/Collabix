from apps.core.models import TimeStampedUUIDModel


class ChatBaseModel(TimeStampedUUIDModel):
    class Meta:
        abstract = True
