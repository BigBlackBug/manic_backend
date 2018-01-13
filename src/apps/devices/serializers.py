import logging

from rest_framework.serializers import ModelSerializer

from src.apps.devices.models import FCMDevice

logger = logging.getLogger(__name__)


class DeviceSerializerMixin(ModelSerializer):
    class Meta:
        fields = (
            "id", "name", "registration_id", "device_id", "active",
            "date_created", "type"
        )
        read_only_fields = ("date_created",)

        extra_kwargs = {"active": {"default": True}}


class FCMDeviceSerializer(ModelSerializer):
    def create(self, validated_data):
        request = self.context['request']
        device = super().create(validated_data)

        user = request.user
        if user.is_master(request):
            logger.info(f'Creating a device for master, id={device.id}, '
                        f'type={device.type}')
            user.master.device = device
            user.master.save()
        elif user.is_client(request):
            logger.info(f'Creating a device for client, id={device.id}, '
                        f'type={device.type}')
            user.client.device = device
            user.client.save()
        return device

    class Meta(DeviceSerializerMixin.Meta):
        model = FCMDevice

        extra_kwargs = {"id": {"read_only": False, "required": False}}
