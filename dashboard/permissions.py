from rest_framework import permissions


class UserPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        elif request.method == "DELETE" and request.user.is_superuser:
            return True
        elif request.method == "POST" and request.user.is_superuser:
            return False
        elif request.method == "PATCH" and obj.creator == request.user or obj.executor == request.user or request.user.is_superuser:
            return True
        return False

    # def has_object_permission(self, request, view, obj):
    #     print(obj.description)
    #     if request.method in permissions.SAFE_METHODS:
    #         return True
    #     elif request.method == "PATCH":
    #         if obj.creator == request.user and obj.executor == request.user:
    #             try:
    #                 if request.status != "Done":
    #                     return True
    #             except AttributeError:
    #                 return True
    #             return False
    #             # try:
    #             #     if request.status:
    #             #         return False
    #             # except AttributeError:
    #             #     return True
    #         # if obj.executor == request.user:
    #         #     try:
    #
    #
    #         # elif obj.executor == request.user and request.status != "Done":
    #         #     return True
    def has_permission(self, request, view):
        return True


class UserReadPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return False

    def has_permission(self, request, view):
        return True
