from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from src.apps.authentication.models import Registration


class RegistrationSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(label=_("Phone"))
    verification_code = serializers.CharField(max_length=4, required=False)

    class Meta:
        model = Registration
        fields = '__all__'

    def validate_phone(self, phone):
        # TODO validate phone
        return phone


class UpdateRegistrationSerializer(serializers.Serializer):
    verification_code = serializers.CharField(required=True, max_length=4)
