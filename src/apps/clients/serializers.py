import logging
import string

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from src.apps.core.models import Location
from src.apps.core.serializers import LocationSerializer
from .models import Client, Address, PaymentCard, ClientStatus

logger = logging.getLogger(__name__)


class AddressSerializer(serializers.ModelSerializer):
    location = LocationSerializer(required=True)
    comment = serializers.CharField(max_length=1024, required=False)

    def create(self, validated_data):
        location = Location.objects.create(**validated_data.pop('location'))
        client = self.context.get('client', None)

        is_default = len(client.addresses.all()) == 0
        return Address.objects.create(location=location, client=client,
                                      is_default=is_default,
                                      **validated_data)

    def update(self, instance, validated_data):
        # manually updating location
        new_location = validated_data.pop('location', None)
        if new_location:
            logger.debug(f'Saving a new location for address {instance.id}')
            location_serializer = LocationSerializer(instance=instance.location,
                                                     data=new_location,
                                                     partial=True)
            location_serializer.is_valid(raise_exception=True)
            instance.location = location_serializer.save()

        # other fields and handled automatically
        return super().update(instance, validated_data)

    class Meta:
        model = Address
        fields = '__all__'


class PaymentCardSerializer(serializers.ModelSerializer):
    def validate_card_number(self, card_number):
        if len(card_number) != 16 and len(card_number) != 19:
            raise ValidationError('Invalid Card Number. Incorrect Length')
        for digit in card_number:
            if digit not in string.digits:
                raise ValidationError('Invalid Card Number. '
                                      'It must only contain digits')
        return card_number

    def create(self, validated_data):
        request = self.context.get('request')
        client = request.user.client
        return PaymentCard.objects.create(client=client, **validated_data)

    class Meta:
        model = PaymentCard
        exclude = ('client',)
        read_only_fields = ('id',)


class ClientSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)
    tip = serializers.IntegerField(min_value=0, max_value=15, required=False)
    date_of_birth = serializers.DateField()
    gender = serializers.CharField(max_length=1)
    first_name = serializers.CharField(max_length=32)
    phone = serializers.CharField(source='user.phone', required=False)
    payment_cards = PaymentCardSerializer(many=True, read_only=True)
    addresses = AddressSerializer(read_only=True, many=True)

    def create(self, validated_data):
        address_data = validated_data.pop('address', None)
        client = self.context['request'].user.client
        client.status = ClientStatus.CREATED
        for (key, value) in validated_data.items():
            setattr(client, key, value)

        if address_data:
            address_serializer = AddressSerializer(data=address_data, context={
                'client': client
            })
            address_serializer.is_valid(raise_exception=True)
            address_serializer.save()
        client.save()
        return client

    def validate_phone(self, phone):
        # TODO validate phone
        return phone

    def update(self, instance, validated_data):
        new_date_of_birth = validated_data.pop('date_of_birth', None)
        new_tip = validated_data.pop('tip', None)
        new_name = validated_data.pop('first_name', None)

        if len(validated_data) != 0:
            raise ValidationError(f'The following fields may not be changed: '
                                  f'{list(validated_data.keys())}')

        if new_name:
            logger.debug(f'Updating name for '
                         f'client {instance.first_name}, id={instance.id}')
            instance.first_name = new_name

        if new_tip:
            logger.debug(f'Updating tip for '
                         f'client {instance.first_name}, id={instance.id}')
            instance.tip = new_tip

        if new_date_of_birth:
            logger.debug(f'Updating date_of_birth for '
                         f'client {instance.first_name}, id={instance.id}')
            instance.date_of_birth = new_date_of_birth

        instance.save()
        return instance

    class Meta:
        model = Client
        fields = (
        'id', 'avatar', 'first_name', 'gender', 'date_of_birth', 'tip',
        'address', 'phone', 'payment_cards', 'addresses')


class SimpleClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('id', 'avatar', 'first_name')
