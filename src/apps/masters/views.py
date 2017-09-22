from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Master
from .serializers import MasterSerializer


class MastersView(generics.ListCreateAPIView):
    view_name = 'masters-list'

    queryset = Master.objects.all()
    serializer_class = MasterSerializer
    # permission_classes = (IsAuthenticated,)
