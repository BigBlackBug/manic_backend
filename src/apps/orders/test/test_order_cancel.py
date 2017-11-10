import datetime

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from src.apps.authentication.models import PhoneAuthUser, Token
from src.apps.masters.models import Master
from src.apps.masters.test import make_everything, make_client, make_order
from src.apps.orders.models import Order
from src.apps.orders.views import CancelOrderView


class CancelOrderTestCase(APITestCase):
    def setUp(self):
        make_everything()
        self.user = PhoneAuthUser.objects.create(phone='777')
        self.client_object = make_client(self.user)
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_cancel_order(self):
        master = Master.objects.get(first_name='VASYA')

        service = master.services.all()[0]
        # manually creating an order
        order_1, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                time=datetime.time(hour=11, minute=00))
        resp = self.client.delete(
            reverse(CancelOrderView.view_name, args=[order_1.id]))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        # two orders
        with self.assertRaises(Order.DoesNotExist):
            Order.objects.get(pk=order_1.id)
