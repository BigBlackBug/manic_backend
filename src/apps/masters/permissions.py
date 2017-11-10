from src.apps.core.permissions import IsMaster


class IsMasterIDCorrect(IsMaster):
    """
    Allows access only to users which are masters and whose id
    matches with url id
    """

    def has_permission(self, request, view):
        return super().has_permission(request, view) and \
               int(view.kwargs['pk']) == request.user.master.id
