from rest_framework.serializers import ModelSerializer

from src.apps.devices.models import FCMDevice


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
            user.master.device = device
            user.master.save()
        elif user.is_client(request):
            user.client.device = device
            user.client.save()
        return device

    class Meta(DeviceSerializerMixin.Meta):
        model = FCMDevice

        extra_kwargs = {"id": {"read_only": False, "required": False}}
