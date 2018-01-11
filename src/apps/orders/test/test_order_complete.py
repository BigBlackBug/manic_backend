import datetime
from unittest import mock

from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from src.apps.authentication.models import PhoneAuthUser, Token
from src.apps.masters.models import Master, Schedule, TimeSlot, Time
from src.apps.orders.models import OrderStatus, Order, CloudPaymentsTransaction, \
    OrderItem, PaymentType
from src.apps.orders.views import CompleteOrderView
from src.utils.object_creation import make_everything, make_client, make_order, \
    make_master, make_category


@mock.patch('src.apps.orders.cloudpayments.client.confirm_payment',
            lambda a, b: True)
class CompleteOrderTestCase(APITestCase):
    def setUp(self):
        make_everything()
        self.user = PhoneAuthUser.objects.create(phone='777')
        master = Master.objects.get(first_name='VASYA')
        token, _ = Token.objects.get_or_create(master=master)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.client_object = make_client(self.user)

    def test_complete_order(self):
        master = Master.objects.get(first_name='VASYA')
        service = master.services.all()[0]
        # manually creating an order
        order_1, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                order_time=datetime.time(hour=11, minute=00))
        order_1.time_started = timezone.now()
        order_1.status = OrderStatus.STARTED
        order_1.transaction = CloudPaymentsTransaction.objects.create(
            transaction_id=1, transaction_info={
                'info': 'yeah'
            })
        order_1.save()
        resp = self.client.patch(
            reverse(CompleteOrderView.view_name, args=[order_1.id]))

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['transaction_id'], 1)
        # TODO test serializers
        order = Order.objects.get(pk=order_1.id)
        self.assertIsNotNone(order.time_taken)
        self.assertEqual(order.status, OrderStatus.DONE)

        master = Master.objects.get(first_name='VASYA')

        self.assertEqual(master.balance.on_hold, service.masters_share(
            self.client_object.tip_multiplier()))

    def test_complete_order_cash(self):
        master = Master.objects.get(first_name='VASYA')
        service = master.services.all()[0]
        # manually creating an order
        order_1, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                order_time=datetime.time(hour=11, minute=00),
                                payment_type=PaymentType.CASH)
        order_1.time_started = timezone.now()
        order_1.status = OrderStatus.STARTED
        order_1.save()
        resp = self.client.patch(
            reverse(CompleteOrderView.view_name, args=[order_1.id]))

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['transaction_id'], None)
        # TODO test serializers
        order = Order.objects.get(pk=order_1.id)
        self.assertIsNotNone(order.time_taken)
        self.assertEqual(order.status, OrderStatus.DONE)

        master = Master.objects.get(first_name='VASYA')

        self.assertEqual(master.balance.on_hold, service.masters_share(
            self.client_object.tip_multiplier()))
        self.assertEqual(master.balance.debt, service.service_share())

    def test_complete_order_4hands(self):
        # creating a new master
        sanya = make_master('SANYA', 100)
        feet = make_category("Педикюр")

        for service in feet.services.all():
            sanya.services.add(service)
        sanya.save()
        # VASYA works on 0,+1, does manicure, got three slots
        schedule = Schedule.objects.create(master=sanya, date=timezone.now())
        schedule.save()

        TimeSlot.objects.create(time=Time.objects.create(hour=10, minute=30),
                                taken=True, schedule=schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=00),
                                taken=False, schedule=schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=30),
                                taken=False, schedule=schedule)

        vasya = Master.objects.get(first_name='VASYA')
        # manually creating an order with two masters and two services
        order_1, _ = make_order(client=self.client_object,
                                order_date=timezone.now(),
                                master=vasya,
                                service=vasya.services.all()[0],
                                order_time=datetime.time(hour=11,
                                                         minute=00))

        schedule = sanya.get_schedule(timezone.now())
        slot = schedule.get_slot(datetime.time(hour=11, minute=00))

        order_item = OrderItem.objects.create(service=sanya.services.all()[0],
                                              master=sanya,
                                              order=order_1,
                                              locked=False)
        slot.order_item = order_item
        slot.taken = True
        slot.save()

        order_1.time_started = timezone.now()
        order_1.status = OrderStatus.STARTED
        order_1.transaction = CloudPaymentsTransaction.objects.create(
            transaction_id=1, transaction_info={
                'info': 'yeah'
            })
        order_1.save()
        resp = self.client.patch(
            reverse(CompleteOrderView.view_name, args=[order_1.id]))

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['transaction_id'], 1)

        order = Order.objects.get(pk=order_1.id)
        self.assertIsNotNone(order.time_taken)
        self.assertEqual(order.status, OrderStatus.DONE)

        vasya = Master.objects.get(first_name='VASYA')
        sanya = Master.objects.get(first_name='SANYA')

        self.assertEqual(vasya.balance.on_hold, int(
            vasya.services.all()[0].masters_share(
                self.client_object.tip_multiplier())))
        self.assertEqual(sanya.balance.on_hold, int(
            sanya.services.all()[0].masters_share(
                self.client_object.tip_multiplier())))
        # TODO добавить больше тестов по разруливанию бабоса
