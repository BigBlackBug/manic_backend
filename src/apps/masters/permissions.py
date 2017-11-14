from src.apps.core.permissions import IsMaster
from .models import MasterStatus


class IsMasterIDCorrect(IsMaster):
    """
    Allows access only to users which are masters and whose id
    matches with url id
    """
    message = "Trying to access someone else's endpoint"

    def has_permission(self, request, view):
        return super().has_permission(request, view) and \
               int(view.kwargs['pk']) == request.user.master.id


class IsMasterVerified(IsMaster):
    """
    Allows access only to users which are masters and whose id
    matches with url id
    """
    message = "Master is unverified, please contact " \
              "the 4hands2go Administrator"

    def has_permission(self, request, view):
        return super().has_permission(request, view) and \
               request.user.master.status == MasterStatus.VERIFIED
