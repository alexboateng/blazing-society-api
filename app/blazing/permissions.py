from rest_framework import permissions


class allowSafeMethods(permissions.BasePermission):
    """Allow only super user to unsafe methods"""

    def has_permission(self, request, view):
        """Check if user is trying to acces safe methods"""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.is_superuser


class UpdateOwnStatus(permissions.BasePermission):
    """Allow users to update their own status"""

    def has_object_permission(self, request, view, obj):
        """Check if user is trying to update own status"""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user_profile.id == request.user.id


class IsNotAuthenticated(permissions.BasePermission):
    """
    Allows access only to non authenticated users.
    """
    def has_permission(self, request, view):
        return not request.user.is_authenticated()