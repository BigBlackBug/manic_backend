from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from src.apps.devices.models import FCMDevice
from src.apps.devices.serializers import FCMDeviceSerializer


class FCMDeviceViewSet(ModelViewSet):
    view_name = 'add-device'
    queryset = FCMDevice.objects.all()
    serializer_class = FCMDeviceSerializer
    permission_classes = (permissions.IsAuthenticated,)

