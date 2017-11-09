from rest_framework.permissions import BasePermission


class IsClient(BasePermission):
    """
    Allows access only to users which are clients
    """
    message = "A user must be a Client to access this endpoint"

    def has_permission(self, request, view):
        return request.user.is_client()


class IsMaster(BasePermission):
    """
    Allows access only to users which are masters
    """
    message = "A user must be a Master to access this endpoint"

    def has_permission(self, request, view):
        return request.user.is_master()


class HasAccount(BasePermission):
    """
    Allows access only to users who have an account
    """
    message = "A user must be either a Master or a Client to access " \
              "this endpoint"

    def has_permission(self, request, view):
        return request.user.has_account()
