from rest_framework import serializers

from src.apps.core.models import Location
from src.apps.core.serializers import LocationSerializer
from .models import Client, Address


class AddressSerializer(serializers.ModelSerializer):
    location = LocationSerializer(required=True)

    def create(self, validated_data):
        location = Location.objects.create(**validated_data.pop('location'))
        return Address.objects.create(location=location, **validated_data)

    class Meta:
        model = Address
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=True)
    tip = serializers.IntegerField(min_value=0, max_value=15, required=True)
    date_of_birth = serializers.DateField(required=True)
    gender = serializers.CharField(max_length=1, required=True)
    first_name = serializers.CharField(max_length=32, required=True)

    def create(self, validated_data):
        address_serializer = AddressSerializer(data=validated_data.pop('address'))
        address_serializer.is_valid(raise_exception=True)
        address = address_serializer.save()
        return Client.objects.create(user=self.context['request'].user,
                                     address=address,
                                     **validated_data)

    # TODO update
    def update(self, instance, validated_data):
        raise NotImplementedError()

    class Meta:
        model = Client
        fields = ('first_name', 'gender', 'date_of_birth', 'tip', 'address')
