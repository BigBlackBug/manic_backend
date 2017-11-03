# -*- coding: utf-8 -*-

from django.db import models

from src.apps.authentication.models import UserProfile
from src.apps.core.models import Location


class Client(UserProfile):
    # FK fields
    # orders
    # payment_cards
    # addresses

    tip = models.IntegerField(default=5)

    @property
    def home_address(self):
        if len(self.addresses.all()) == 0:
            return None
        # TODO rewrite. This is bad
        for address in self.addresses.all():
            if address.is_default:
                return address
        raise ValueError("A client must have a home address")

    def __str__(self):
        return f'Client. {super().__str__()}'

    class Meta(UserProfile.Meta):
        db_table = 'client'


class Address(models.Model):
    location = models.OneToOneField(Location, on_delete=models.CASCADE,
                                    related_name='+')
    client = models.ForeignKey(Client, on_delete=models.CASCADE,
                               related_name='addresses', null=True)

    city = models.CharField(max_length=64)
    street_name = models.CharField(max_length=64)
    building = models.CharField(max_length=16)
    floor = models.IntegerField()
    apt_number = models.IntegerField()
    entrance = models.IntegerField()
    has_intercom = models.BooleanField()
    is_default = models.BooleanField()

    def __str__(self):
        return f'{self.city}, {self.street_name}, apt. {self.apt_number}, ' \
               f'home: {self.home_address}'


class PaymentCard(models.Model):
    # TODO is it 64?? check back
    cryptogram = models.CharField(max_length=64)
    client_name_on_card = models.CharField(max_length=64)
    card_number = models.CharField(max_length=19)
    client = models.ForeignKey(Client, on_delete=models.CASCADE,
                               related_name='payment_cards')

    def __str__(self):
        return f'Card {self.id} of {self.client.id}'
