from rest_framework import permissions

from apps.accounts.models import Role


def is_admin(user) -> bool:
    return bool(user and user.is_authenticated and (user.is_staff or user.groups.filter(name=Role.ADMIN).exists()))


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        return is_admin(request.user)
