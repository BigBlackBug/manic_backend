# -*- coding: utf-8 -*-
import logging

from django.contrib.postgres.fields import HStoreField
from django.db import models
from django.utils import timezone

from src.apps.categories.models import Service
from src.apps.clients.models import Client
from src.apps.finances.models import TransactionEntry, TransactionEntryType
from src.apps.masters.models import Master
from src.apps.orders import notifications

logger = logging.getLogger(__name__)


class OrderStatus:
    CREATED = 'CREATED'
    ACTIVATED = 'ACTIVATED'
    STARTED = 'STARTED'
    DONE = 'DONE'
    CHOICES = (
        (CREATED, 'Создан'),
        (ACTIVATED, 'Принят Мастером'),
        (STARTED, 'Начат'),
        (DONE, 'Завершён'),
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
        max_length=10,
        choices=OrderStatus.CHOICES,
        default=OrderStatus.CREATED,
    )

    time_started = models.DateTimeField(null=True)
    time_taken = models.DurationField(null=True)

    comment = models.CharField(max_length=1024, blank=True)

    # TODO create property on save
    @property
    def total_cost(self):
        """
        Returns a total cost of the order, combined from costs
        of each individual service and the client's tips
        """
        # TODO value may be taken from 'special'
        return sum(map(
            lambda item: int(
                item.service.cost * (1 + self.client.tip_multiplier())),
            self.order_items.all()))

    def activate(self):
        self.status = OrderStatus.ACTIVATED
        for item in self.order_items:
            if item.master.device:
                logger.info(f'Order {self.id} created. '
                            f'Sending NEW_ORDER notification '
                            f'to master {item.master.first_name}')
                item.master.device.send_message(
                    notifications.NEW_ORDER_TITLE,
                    notifications.NEW_ORDER_CONTENT(
                        order_time=self.time.strftime('%H:%M'),
                        order_date=self.date.strftime('%Y-%m-%d')),
                    data={
                        'event': notifications.NEW_ORDER_EVENT,
                        'order_id': self.id
                    })

    def start(self):
        logger.info(f'Starting order {self.id}')
        self.status = OrderStatus.STARTED
        self.time_started = timezone.now()

    def complete(self):
        """
        Sets the `status` and `time_taken` of the order
        and adjusts balance of each involved master
        """
        logger.info(f'Completing order {self.id}')
        self.status = OrderStatus.DONE
        self.time_taken = timezone.now() - self.time_started

        for item in self.order_items.all():
            # needed by analytics
            TransactionEntry.objects.create(entry_type=TransactionEntryType.IN,
                                            master=item.master,
                                            value=item.service.service_share(),
                                            order=self)
            item.master.complete_order_payment(self, item)
            item.master.save()

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

    locked = models.BooleanField()
