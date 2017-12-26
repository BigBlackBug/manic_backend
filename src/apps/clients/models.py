# -*- coding: utf-8 -*-

from django.db import models

from src.apps.authentication.models import UserProfile
from src.apps.core.models import Location


class ClientStatus:
    DUMMY = 'DUMMY'
    VERIFIED = 'VERIFIED'

    CHOICES = (
        (DUMMY, 'Свежий аккаунт'),
        (VERIFIED, 'Подтверждён'),
    )


class Client(UserProfile):
    # FK fields
    # orders
    # payment_cards
    # addresses
    # device

    tip = models.IntegerField(default=5)
    status = models.CharField(max_length=9,
                              choices=ClientStatus.CHOICES,
                              default=ClientStatus.DUMMY)

    def tip_multiplier(self):
        return 1 + self.tip / 100.0

    def activated(self):
        return self.status == ClientStatus.VERIFIED

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
    comment = models.CharField(max_length=1024, blank=True)
    is_default = models.BooleanField()

    def __str__(self):
        return f'{self.city}, {self.street_name}, apt. {self.apt_number}, ' \
               f'is_default: {self.is_default}'


class PaymentCard(models.Model):
    cryptogram = models.CharField(max_length=512)
    client_name_on_card = models.CharField(max_length=64)
    card_number = models.CharField(max_length=19)
    client = models.ForeignKey(Client, on_delete=models.CASCADE,
                               related_name='payment_cards')

    def __str__(self):
        return f'Card #{self.id}, **{self.card_number[-4:]}' \
               f' of client_id: {self.client.id}'
