from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from django.db.models import Q

User = get_user_model()


class EmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            # Normalize email address by converting it to lowercase
            user = User.objects.get(Q(email__iexact=email))
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
