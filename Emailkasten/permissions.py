from rest_framework.permissions import IsAdminUser
from .LoggerFactory import LoggerFactory

class IsAdminOrSelf(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user or request.user.is_staff)

    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_staff) or request.user == obj
