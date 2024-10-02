from rest_framework.permissions import IsAdminUser

class IsAdminOrSelf(IsAdminUser):
    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_staff) or request.user == obj
