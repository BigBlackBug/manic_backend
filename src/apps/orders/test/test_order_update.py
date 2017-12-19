import datetime

from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from src.apps.authentication.models import PhoneAuthUser, Token
from src.apps.masters.models import Master
from src.apps.orders.models import OrderStatus, Order, PaymentType
from src.apps.orders.views import OrderUpdateCommentView
from src.utils.object_creation import make_everything, make_client, make_order


class UpdateOrderCommentTestCase(APITestCase):
    def setUp(self):
        make_everything()
        self.user = PhoneAuthUser.objects.create(phone='777')
        self.client_object = make_client(self.user)
        token, _ = Token.objects.get_or_create(client=self.client_object)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_add_comment(self):
        master = Master.objects.get(first_name='VASYA')
        service = master.services.all()[0]
        # manually creating an order
        order_1, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                order_time=datetime.time(hour=11, minute=00),
                                payment_type=PaymentType.CASH)
        order_1.time_started = timezone.now()
        order_1.status = OrderStatus.DONE
        order_1.save()

        self.assertEqual(order_1.comment, '')
        resp = self.client.patch(
            reverse(OrderUpdateCommentView.view_name, args=[order_1.id]), data={
                'comment': 'A new comment'
            }, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        order = Order.objects.get(pk=order_1.id)
        self.assertEqual(order.comment, 'A new comment')

    def test_update_comment(self):
        master = Master.objects.get(first_name='VASYA')
        service = master.services.all()[0]
        # manually creating an order
        # manually creating an order
        order_1, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                order_time=datetime.time(hour=11, minute=00),
                                payment_type=PaymentType.CASH,
                                comment='LOL')
        order_1.time_started = timezone.now()
        order_1.status = OrderStatus.DONE
        order_1.save()

        self.assertEqual(order_1.comment, 'LOL')
        resp = self.client.patch(
            reverse(OrderUpdateCommentView.view_name, args=[order_1.id]), data={
                'comment': 'A new comment'
            }, format='json')

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        order = Order.objects.get(pk=order_1.id)
        self.assertEqual(order.comment, 'A new comment')

    def test_unable_to_update(self):
        master = Master.objects.get(first_name='VASYA')
        service = master.services.all()[0]
        # manually creating an order
        order_1, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                order_time=datetime.time(hour=11, minute=00),
                                comment='old')
        order_1.time_started = timezone.now()
        order_1.status = OrderStatus.STARTED
        order_1.save()

        self.assertEqual(order_1.comment, 'old')
        resp = self.client.patch(
            reverse(OrderUpdateCommentView.view_name, args=[order_1.id]), data={
                'comment': 'new'
            }, format='json')

        # order is not DONE
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
