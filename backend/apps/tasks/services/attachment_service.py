from django.db import transaction

from ..models import TaskActivity, TaskAttachment
from ._helpers import employee_for_user
from .activity_service import TaskActivityService


class TaskAttachmentService:
    @staticmethod
    @transaction.atomic
    def create(*, task, uploaded_file, user=None, request=None):
        actor = employee_for_user(user)
        attachment = TaskAttachment.objects.create(
            task=task,
            uploaded_by=actor,
            file=uploaded_file,
            original_filename=uploaded_file.name,
        )
        TaskActivityService.record(
            task=task,
            actor=actor,
            activity_type=TaskActivity.Type.ATTACHED,
            message="attached file to task",
            new_value={"filename": attachment.original_filename},
        )
        return attachment
