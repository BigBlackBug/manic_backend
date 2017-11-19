from datetime import timedelta

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from src.apps.authentication.models import Registration


class RegistrationSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(label=_("Phone"))
    verification_code = serializers.CharField(max_length=4, required=False)
    expires = serializers.DateTimeField(read_only=True)
    type = serializers.CharField(max_length=6)

    REGISTRATION_LIFETIME = timedelta(minutes=5)

    class Meta:
        model = Registration
        fields = '__all__'

    def validate_phone(self, phone):
        # TODO validate phone
        return phone

    def create(self, validated_data):
        expires = timezone.now() + RegistrationSerializer.REGISTRATION_LIFETIME
        return Registration.objects.create(**validated_data, expires=expires)


class UpdateRegistrationSerializer(serializers.Serializer):
    verification_code = serializers.CharField(required=True, max_length=4)
