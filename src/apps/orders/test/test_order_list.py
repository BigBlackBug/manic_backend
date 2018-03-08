import datetime
from datetime import timedelta as delta

from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from src.apps.authentication.models import PhoneAuthUser, Token
from src.apps.core import utils
from src.apps.masters.models import Master, Schedule, TimeSlot
from src.apps.masters.receivers import *
from src.apps.orders.models import OrderStatus
from src.apps.orders.views import OrderListCreateView
from src.utils.object_creation import make_everything, make_client, make_order


class ListOrderTestCase(APITestCase):
    def setUp(self):
        make_everything()
        self.user = PhoneAuthUser.objects.create(phone='777')
        self.client_object = make_client(self.user)
        token, _ = Token.objects.get_or_create(client=self.client_object)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_list_client_orders(self):
        master = Master.objects.get(first_name='VASYA')
        schedule = master.get_schedule(timezone.now() + delta(days=2))
        schedule.delete()
        schedule = Schedule.objects.create(master=master,
                                           date=timezone.now() + delta(days=2))
        schedule.save()

        TimeSlot.objects.create(time=Time.objects.create(hour=12, minute=30),
                                taken=False, schedule=schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=13, minute=00),
                                taken=False, schedule=schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=13, minute=30),
                                taken=False, schedule=schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=14, minute=00),
                                taken=False, schedule=schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=14, minute=30),
                                taken=False, schedule=schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=15, minute=00),
                                taken=False, schedule=schedule)
        service = master.services.all()[0]
        # manually creating an order
        order_1, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                order_date=utils.get_date(1),
                                order_time=datetime.time(hour=11, minute=00))
        # manually creating an order
        order_2, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                order_date=utils.get_date(2),
                                order_time=datetime.time(hour=12, minute=30))

        order_2, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                order_date=utils.get_date(2),
                                order_time=datetime.time(hour=14, minute=30))

        order_3, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                order_date=utils.get_date(1),
                                order_time=datetime.time(hour=11, minute=30),
                                status=OrderStatus.DONE)
        resp = self.client.get(reverse(OrderListCreateView.view_name))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # two orders
        # TODO test serializers
        active = resp.data['active']
        history = resp.data['history']
        self.assertEqual(len(active), 3)
        self.assertEqual(len(history), 1)

    def test_list_master_orders(self):
        master = Master.objects.get(first_name='VASYA')
        # logging in as a master
        token, _ = Token.objects.get_or_create(master=master)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        service = master.services.all()[0]
        # manually creating an order
        order_1, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                order_date=utils.get_date(1),
                                order_time=datetime.time(hour=11, minute=00))
        # manually creating an order
        order_2, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                order_date=utils.get_date(1),
                                order_time=datetime.time(hour=12, minute=00))

        resp = self.client.get(reverse(OrderListCreateView.view_name))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # two orders
        # TODO test serializers
        active = resp.data['active']
        history = resp.data['history']
        self.assertEqual(len(active), 2)
