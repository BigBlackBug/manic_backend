from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from src.apps.core.models import Location
from src.apps.core.serializers import LocationSerializer
from .models import Client, Address


class AddressSerializer(serializers.ModelSerializer):
    location = LocationSerializer(required=True)

    def create(self, validated_data):
        location = Location.objects.create(**validated_data.pop('location'))
        return Address.objects.create(location=location, **validated_data)

    def update(self, instance, validated_data):
        # manually updating location
        new_location = validated_data.pop('location', None)
        if new_location:
            location_serializer = LocationSerializer(instance=instance.location,
                                                     data=new_location, partial=True)
            location_serializer.is_valid(raise_exception=True)
            instance.location = location_serializer.save()

        # other fields and handled automatically
        return super().update(instance, validated_data)

    class Meta:
        model = Address
        fields = '__all__'


class ClientSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)
    tip = serializers.IntegerField(min_value=0, max_value=15, required=False)
    date_of_birth = serializers.DateField()
    gender = serializers.CharField(max_length=1)
    first_name = serializers.CharField(max_length=32)
    phone = serializers.CharField(source='user.phone', required=False)

    def create(self, validated_data):
        address = None
        if 'address' in validated_data:
            address_serializer = AddressSerializer(data=validated_data.pop('address'))
            address_serializer.is_valid(raise_exception=True)
            address = address_serializer.save()

        return Client.objects.create(user=self.context['request'].user,
                                     address=address,
                                     **validated_data)

    def validate_phone(self, phone):
        # TODO validate phone
        return phone

    def update(self, instance, validated_data):
        new_address = validated_data.pop('address', None)
        new_phone = validated_data.pop('user', {}).pop('phone', None)
        new_tip = validated_data.pop('tip', None)

        if len(validated_data) != 0:
            raise ValidationError(f'The following fields may not be changed: {validated_data.keys()}')

        if new_address:
            address_serializer = AddressSerializer(instance=instance.address,
                                                   data=new_address, partial=True)
            address_serializer.is_valid(raise_exception=True)
            # partial update of address
            instance.address = address_serializer.save()
        if new_phone:
            instance.user.phone = new_phone
            instance.user.save()

        if new_tip:
            instance.tip = new_tip

        instance.save()
        return instance

    class Meta:
        model = Client
        fields = ('first_name', 'gender', 'date_of_birth', 'tip', 'address', 'phone')
