from rest_framework.permissions import BasePermission


class IsClient(BasePermission):
    """
    Allows access only to users which are clients
    """

    def has_permission(self, request, view):
        return request.user.is_client()
