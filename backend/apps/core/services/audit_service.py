from apps.core.models import AuditLog


class AuditService:
    @staticmethod
    def log_create(*, user, instance, new_data=None, ip_address=None):
        return AuditService._log(
            user=user,
            action="create",
            instance=instance,
            new_data=new_data,
            ip_address=ip_address,
        )

    @staticmethod
    def log_update(*, user, instance, old_data=None, new_data=None, ip_address=None):
        return AuditService._log(
            user=user,
            action="update",
            instance=instance,
            old_data=old_data,
            new_data=new_data,
            ip_address=ip_address,
        )

    @staticmethod
    def log_delete(*, user, instance, old_data=None, ip_address=None):
        return AuditService._log(
            user=user,
            action="delete",
            instance=instance,
            old_data=old_data,
            ip_address=ip_address,
        )

    @staticmethod
    def log_status_change(*, user, instance, old_status, new_status, ip_address=None):
        return AuditService._log(
            user=user,
            action="status_change",
            instance=instance,
            old_data={"status": old_status},
            new_data={"status": new_status},
            ip_address=ip_address,
        )

    @staticmethod
    def _log(*, user, action, instance, old_data=None, new_data=None, ip_address=None):
        return AuditLog.objects.create(
            user=user if getattr(user, "is_authenticated", False) else None,
            action=action,
            model_name=instance.__class__.__name__,
            object_id=str(instance.pk),
            old_data=old_data,
            new_data=new_data,
            ip_address=ip_address,
        )
