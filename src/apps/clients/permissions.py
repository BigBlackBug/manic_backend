from src.apps.core.permissions import IsClient


class IsClientIDCorrect(IsClient):
    """
    Allows access only to users which are clients and whose id
    matches with url id
    """
    message = "Trying to access someone else's endpoint"

    def has_permission(self, request, view):
        return super().has_permission(request, view) and \
               int(view.kwargs['pk']) == request.user.client.id
