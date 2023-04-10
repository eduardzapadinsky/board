from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    """
    Permissions for different users

    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.method == "POST" and not request.user.is_superuser:
            return True
        elif request.method == "DELETE" and request.user.is_superuser:
            return True
        elif request.method == "PATCH":
            print(obj.creator)
            print(obj.executor)
            print(request.user)
            print(obj.creator == request.user)
            print(obj.executor == request.user)
            print(request.user.is_superuser)
            if obj.creator == request.user or obj.executor == request.user or request.user.is_superuser:
                print("yes")
                return True
        return False

    def has_permission(self, request, view):
        if request.method == 'POST' and request.user.is_superuser:
            return False
        elif request.method == "DELETE" and not request.user.is_superuser:
            return False
        return True


class UserReadPermission(permissions.BasePermission):
    """
    Permissions for users to read only

    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return False

    def has_permission(self, request, view):
        return True
