# -*- coding: utf-8 -*-

from django.contrib.postgres.fields import HStoreField
from django.db import models

from src.apps.categories.models import Service
from src.apps.clients.models import Client
from src.apps.masters.models import Master


class OrderStatus:
    CREATED = 'CREATED'
    ACCEPTED = 'ACCEPTED'
    DONE = 'DONE'
    CHOICES = (
        (CREATED, 'Создан'),
        (ACCEPTED, 'Принят Мастером'),
        (DONE, 'Завершён')
    )


class PaymentType:
    CARD = 'CARD'
    CASH = 'CASH'
    CHOICES = (
        (CARD, 'Карта'),
        (CASH, 'Наличные')
    )


class CPTransactionStatus:
    CREATED = 'CREATED'
    FINISHED = 'FINISHED'
    S3D_FAILED = 'S3D_FAILED'
    CHOICES = (
        (CREATED, 'Создана'),
        (FINISHED, 'Завершена'),
        (S3D_FAILED, 'Ошибка верификации Secure 3D')
    )


class CloudPaymentsTransaction(models.Model):
    # FK fields
    # order

    # TODO add index
    transaction_id = models.IntegerField(unique=True)
    transaction_info = HStoreField()
    status = models.CharField(
        max_length=10,
        choices=CPTransactionStatus.CHOICES,
        default=CPTransactionStatus.CREATED,
    )

    def confirm(self):
        self.status = CPTransactionStatus.FINISHED

    def __str__(self):
        return f'{self.transaction_id}'


class Order(models.Model):
    # FK fields
    # order_items

    client = models.ForeignKey(Client, on_delete=models.SET_NULL,
                               related_name='orders', null=True)
    # these are unrelated to schedule
    date = models.DateField()
    time = models.TimeField()

    special = HStoreField(blank=True, null=True)
    payment_type = models.CharField(
        max_length=4,
        choices=PaymentType.CHOICES,
        default=PaymentType.CARD,
    )

    transaction = models.OneToOneField(CloudPaymentsTransaction,
                                       on_delete=models.SET_NULL,
                                       related_name='order',
                                       null=True, blank=True)

    status = models.CharField(
        max_length=8,
        choices=OrderStatus.CHOICES,
        default=OrderStatus.CREATED,
    )

    # TODO create property on save
    @property
    def total_cost(self):
        """
        Returns a total cost of the order, combined from costs
        of each individual service
        """
        # TODO value may be taken from 'special'
        return sum(map(lambda item: item.service.cost,
                       self.order_items.all()))

    def __str__(self):
        return f'Order for client_id: {self.client.id} on' \
               f' {self.date}, {self.time}'


class OrderItem(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE,
                                related_name='+')

    master = models.ForeignKey(Master, on_delete=models.CASCADE,
                               related_name='order_items')

    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name='order_items')
