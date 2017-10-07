# -*- coding: utf-8 -*-
from django.contrib.postgres.fields import HStoreField
from django.db import models

from src.apps.categories.models import Service
from src.apps.clients.models import Client
from src.apps.masters.models import Master


class Order(models.Model):
    # FK fields
    # order_items

    client = models.ForeignKey(Client, on_delete=models.SET_NULL,
                               related_name='orders', null=True)
    # these are unrelated to schedule
    date = models.DateField()
    time = models.TimeField()

    special = HStoreField(blank=True, null=True)

    def __str__(self):
        return f'Order for client_id: {self.client.id} on {self.date}, {self.time}'


class OrderItem(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE,
                                related_name='+')

    master = models.ForeignKey(Master, on_delete=models.CASCADE,
                               related_name='order_items')

    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name='order_items')
