import datetime

from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from src.apps.authentication.models import PhoneAuthUser, Token
from src.apps.masters.models import Master
from src.apps.masters.test import make_everything, make_client, make_order


class MasterTestCase(APITestCase):
    def setUp(self):
        make_everything()
        self.user = PhoneAuthUser.objects.create(phone='777')
        self.client_object = make_client(self.user)
        token, _ = Token.objects.get_or_create(client=self.client_object)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_served_once(self):
        master = Master.objects.get(first_name='VASYA')
        service = master.services.all()[0]
        # manually creating an order
        order_client = make_client()
        # manually creating an order
        make_order(client=order_client, master=master, service=service,
                   time=datetime.time(hour=10, minute=30))

        self.assertEqual(master.times_served(order_client), 1)

    def test_not_served(self):
        master = Master.objects.get(first_name='VASYA')
        service = master.services.all()[0]
        # manually creating an order
        order_client = make_client()
        # manually creating an order
        make_order(client=order_client, master=master, service=service,
                   time=datetime.time(hour=10, minute=30))

        # different client
        self.assertEqual(master.times_served(self.client_object), 0)
