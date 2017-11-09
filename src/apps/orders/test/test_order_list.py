import datetime

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from src.apps.authentication.models import PhoneAuthUser, Token
from src.apps.masters.models import Master
from src.apps.masters.test import make_everything, make_client, make_order
from src.apps.orders.models import OrderStatus
from src.apps.orders.views import OrderListCreateView


class ListOrderTestCase(APITestCase):
    def setUp(self):
        make_everything()
        self.user = PhoneAuthUser.objects.create(phone='777')
        self.client_object = make_client(self.user)
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_list_client_orders(self):
        master = Master.objects.get(first_name='VASYA')
        service = master.services.all()[0]
        # manually creating an order
        order_1, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                time=datetime.time(hour=11, minute=00))
        # manually creating an order
        order_2, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                time=datetime.time(hour=12, minute=00))

        order_3, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                time=datetime.time(hour=11, minute=30),
                                status=OrderStatus.DONE)
        resp = self.client.get(reverse(OrderListCreateView.view_name))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # two orders
        # TODO test serializers
        active = resp.data['active']
        history = resp.data['history']
        self.assertEqual(len(active), 2)
        self.assertEqual(len(history), 1)

    def test_list_master_orders(self):
        master = Master.objects.get(first_name='VASYA')
        # logging in as a master
        token, _ = Token.objects.get_or_create(user=master.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        service = master.services.all()[0]
        # manually creating an order
        order_1, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                time=datetime.time(hour=11, minute=00))
        # manually creating an order
        order_2, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                time=datetime.time(hour=12, minute=00))

        resp = self.client.get(reverse(OrderListCreateView.view_name))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # two orders
        # TODO test serializers
        active = resp.data['active']
        history = resp.data['history']
        self.assertEqual(len(active), 2)
