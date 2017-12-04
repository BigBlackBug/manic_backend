from rest_framework.permissions import BasePermission

from src.apps.authentication.utils import get_admin_user_model


class IsClient(BasePermission):
    """
    Allows access only to users which are clients
    """
    message = "A user must be a Client to access this endpoint"

    def has_permission(self, request, view):
        return request.user.is_client(request)


class IsMaster(BasePermission):
    """
    Allows access only to users which are masters
    """
    message = "A user must be a Master to access this endpoint"

    def has_permission(self, request, view):
        return request.user.is_master(request)


class IsAdmin(BasePermission):
    """
    Allows access only to users which are administrators
    """
    message = "A user must be an Admin to access this endpoint"

    def has_permission(self, request, view):
        return isinstance(request.user, get_admin_user_model())


class IsAccountVerified(BasePermission):
    message = "Your account should be Verified in order to access this page"

    def has_permission(self, request, view):
        if request.user.is_client(request) and request.user.client.activated():
            return True
        elif request.user.is_master(
                request) and request.user.master.activated():
            return True
        return False
