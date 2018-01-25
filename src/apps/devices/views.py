import logging

from rest_framework import permissions, generics, mixins, status
from rest_framework.response import Response

from src.apps.devices.models import FCMDevice
from src.apps.devices.serializers import FCMDeviceSerializer

logger = logging.getLogger(__name__)


class FCMAddDeviceView(mixins.CreateModelMixin,
                       generics.GenericAPIView):
    view_name = 'add-device'
    queryset = FCMDevice.objects.all()
    serializer_class = FCMDeviceSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """
        Attaches or replaces a device of a client/master
        that will receive notifications

        Input:
        ```
        {
          'registration_id':'a super long token',
          'type':'ios/android'
        }
        ```

        Response:

        201 Created
        """
        return super().create(request, *args, **kwargs)


class FCMRemoveDeviceView(mixins.DestroyModelMixin,
                          generics.GenericAPIView):
    view_name = 'remove-device'
    queryset = FCMDevice.objects.all()
    serializer_class = FCMDeviceSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        """
        Detaches a device from a client/master

        Response:

        204 No Content
        """
        device = self.get_object()

        user = request.user
        if user.is_master(request):
            logger.info(f'Deleting a device for master, id={device.id}, '
                        f'type={device.type}')
            user.master.device.delete()
        elif user.is_client(request):
            logger.info(f'Creating a device for client, id={device.id}, '
                        f'type={device.type}')
            user.client.device.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
