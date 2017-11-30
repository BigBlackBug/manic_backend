import datetime
from unittest import mock

from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from src.apps.authentication.models import PhoneAuthUser, Token
from src.apps.masters.models import Master
from src.utils.object_creation import make_everything, make_client, make_order
from src.apps.orders.models import OrderStatus, Order, CloudPaymentsTransaction
from src.apps.orders.views import CompleteOrderView


@mock.patch('src.apps.orders.cloudpayments.confirm',
            lambda phone: True)
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
        # two orders
        # TODO test serializers
        order = Order.objects.get(pk=order_1.id)
        self.assertIsNotNone(order.time_taken)
        self.assertEqual(order.status, OrderStatus.DONE)
