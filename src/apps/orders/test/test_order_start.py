import datetime

from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from src.apps.authentication.models import PhoneAuthUser, Token
from src.apps.core import utils
from src.apps.masters.models import Master
from src.apps.orders.models import OrderStatus, Order
from src.apps.orders.views import StartOrderView
from src.utils.object_creation import make_everything, make_client, make_order


class StartOrderTestCase(APITestCase):
    def setUp(self):
        make_everything()
        self.user = PhoneAuthUser.objects.create(phone='777')
        master = Master.objects.get(first_name='VASYA')
        token, _ = Token.objects.get_or_create(master=master)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.client_object = make_client(self.user)

    def test_start_order(self):
        master = Master.objects.get(first_name='VASYA')
        service = master.services.all()[0]
        # manually creating an order
        order_date = utils.get_date(1, format_string=False)
        order_1, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                order_date=order_date,
                                order_time=datetime.time(hour=11, minute=00))
        # we can only start it on the right day
        frozen = freeze_time(order_date.replace(hour=10, minute=30))
        frozen.start()
        resp = self.client.patch(
            reverse(StartOrderView.view_name, args=[order_1.id]))
        frozen.stop()
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        # two orders
        # TODO test serializers
        order = Order.objects.get(pk=order_1.id)
        self.assertEqual(order.status, OrderStatus.STARTED)
        self.assertIsNotNone(order.time_started)
