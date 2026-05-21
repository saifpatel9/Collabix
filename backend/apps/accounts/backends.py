from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get("email") or username
        if not email or not password:
            return None

        UserModel = get_user_model()
        try:
            user = UserModel._default_manager.get(email__iexact=email)
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
