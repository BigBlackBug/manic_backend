from rest_framework.permissions import BasePermission


class IsClient(BasePermission):
    """
    Allows access only to users which are clients and whose id matches with url id
    """

    def has_permission(self, request, view):
        return request.user.is_client() and \
               int(view.kwargs['pk']) == request.user.client.id

