# -*- coding: utf-8 -*-

from django.db import models

from src.apps.authentication.models import UserProfile
from src.apps.core.models import Location


class Address(models.Model):
    # FK fields
    # client
    location = models.OneToOneField(Location, on_delete=models.CASCADE,
                                    related_name='+')
    city = models.CharField(max_length=64)
    street_name = models.CharField(max_length=64)
    building = models.CharField(max_length=16)
    floor = models.IntegerField()
    apt_number = models.IntegerField()
    entrance = models.IntegerField()
    has_intercom = models.BooleanField()


class Client(UserProfile):
    # FK fields
    # orders
    # payment_cards

    tip = models.IntegerField(default=5)

    address = models.OneToOneField(Address, on_delete=models.CASCADE,
                                   related_name='client', blank=True, null=True)

    class Meta(UserProfile.Meta):
        db_table = 'client'


class PaymentCard(models.Model):
    # TODO is it 64?? check back
    cryptogram = models.CharField(max_length=64)
    client_name_on_card = models.CharField(max_length=64)
    card_number = models.CharField(max_length=19)
    client = models.ForeignKey(Client, on_delete=models.CASCADE,
                               related_name='payment_cards')
