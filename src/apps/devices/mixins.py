from .settings import FCM_DJANGO_SETTINGS as SETTINGS
from rest_framework import permissions

from src.apps.devices.models import FCMDevice


class DeviceViewSetMixin(object):
    lookup_field = "registration_id"

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)

            if (SETTINGS["ONE_DEVICE_PER_USER"] and
                    self.request.data.get('active', True)):
                FCMDevice.objects.filter(user=self.request.user).update(
                    active=False)

        return super(DeviceViewSetMixin, self).perform_create(serializer)

    def perform_update(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)

            if (SETTINGS["ONE_DEVICE_PER_USER"] and
                    self.request.data.get('active', False)):
                FCMDevice.objects.filter(user=self.request.user).update(
                    active=False)

        return super(DeviceViewSetMixin, self).perform_update(serializer)
