from django.db import transaction


class ProfileService:
    @staticmethod
    @transaction.atomic
    def update_profile(*, user, cleaned_data):
        for field in ("full_name", "phone", "profile_image"):
            if field in cleaned_data:
                setattr(user, field, cleaned_data[field])
        user.save(update_fields=["full_name", "phone", "profile_image", "updated_at"])
        return user
