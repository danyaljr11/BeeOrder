# permissions.py
from rest_framework.permissions import BasePermission
from rest_framework.authtoken.models import Token


class TokenRequiredPermission(BasePermission):
    def has_permission(self, request, view):
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            try:
                token_obj = Token.objects.get(key=token)
                if token_obj:
                    return True
            except Token.DoesNotExist:
                pass
        return False


class IsRestaurantManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'restaurant_manager'