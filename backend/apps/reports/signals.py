import logging

from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.attendance.models import Attendance, LeaveRequest
from apps.employees.models import EmployeeProfile
from apps.projects.models import Milestone, Project
from apps.reports.models import ReportConfig, ReportExport
from apps.tasks.models import Task

logger = logging.getLogger(__name__)


def invalidate_analytics_cache():
    try:
        if hasattr(cache, "delete_pattern"):
            cache.delete_pattern("analytics:*")
        else:
            cache.clear()
    except Exception as e:
        logger.warning(f"Cache invalidation failed: {e}")


@receiver([post_save, post_delete], sender=EmployeeProfile)
@receiver([post_save, post_delete], sender=Project)
@receiver([post_save, post_delete], sender=Task)
@receiver([post_save, post_delete], sender=Attendance)
@receiver([post_save, post_delete], sender=LeaveRequest)
@receiver([post_save, post_delete], sender=Milestone)
@receiver([post_save, post_delete], sender=ReportConfig)
@receiver([post_save, post_delete], sender=ReportExport)
def analytics_invalidation_handler(sender, **kwargs):
    invalidate_analytics_cache()
