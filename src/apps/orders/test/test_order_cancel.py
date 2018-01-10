import datetime

from django.utils import timezone
from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from src.apps.authentication.models import PhoneAuthUser, Token
from src.apps.core import utils
from src.apps.masters.models import Master
from src.apps.orders.models import Order
from src.apps.orders.views import OrderCancelView
from src.utils.object_creation import make_everything, make_client, \
    make_order_services, make_order


class MasterCancelOrderTestCase(APITestCase):
    def setUp(self):
        make_everything()
        self.user = PhoneAuthUser.objects.create(phone='777')
        self.client_object = make_client(self.user)
        self.master_object = Master.objects.get(first_name='VASYA')

        token, _ = Token.objects.get_or_create(master=self.master_object)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_cancel_order_many_services_one_master(self):
        services = self.master_object.services.all()
        # manually creating an order

        order_1 = make_order_services(client=self.client_object,
                                      master=self.master_object,
                                      services=services,
                                      order_date=timezone.now(),
                                      order_time=datetime.time(hour=11,
                                                               minute=00))

        frozen = freeze_time(timezone.now().replace(hour=7, minute=0))
        frozen.start()
        resp = self.client.delete(
            reverse(OrderCancelView.view_name, args=[order_1.id]))
        frozen.stop()

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # two orders canceled -> order is deleted
        with self.assertRaises(Order.DoesNotExist):
            Order.objects.get(pk=order_1.id)

        # find new master
        self.master_object = Master.objects.get(pk=self.master_object.id)
        self.assertEqual(self.master_object.balance.future, 0)


    def test_cancel_order_many_services_two_masters(self):
        # TODO test
        pass

    def test_cancel_order_too_late(self):
        services = self.master_object.services.all()
        # manually creating an order

        order_1 = make_order_services(client=self.client_object,
                                      master=self.master_object,
                                      services=services,
                                      order_date=timezone.now(),
                                      order_time=datetime.time(hour=11,
                                                               minute=00))

        frozen = freeze_time(timezone.now().replace(hour=9, minute=0))
        frozen.start()
        resp = self.client.delete(
            reverse(OrderCancelView.view_name, args=[order_1.id]))
        frozen.stop()

        # too late
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_cancel_order_locked(self):
        services = self.master_object.services.all()
        # manually creating an order

        order_1 = make_order_services(client=self.client_object,
                                      master=self.master_object,
                                      services=services,
                                      order_date=timezone.now(),
                                      order_time=datetime.time(hour=11,
                                                               minute=00),
                                      locked=True)

        frozen = freeze_time(timezone.now().replace(hour=7, minute=0))
        frozen.start()
        resp = self.client.delete(
            reverse(OrderCancelView.view_name, args=[order_1.id]))
        frozen.stop()

        # too late
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class ClientCancelOrderTestCase(APITestCase):
    def setUp(self):
        make_everything()
        self.user = PhoneAuthUser.objects.create(phone='777')
        self.client_object = make_client(self.user)
        token, _ = Token.objects.get_or_create(client=self.client_object)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_cancel_order(self):
        master = Master.objects.get(first_name='VASYA')

        service = master.services.all()[0]
        # manually creating an order
        order_1, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                order_date=utils.get_date(1),
                                order_time=datetime.time(hour=12, minute=30))
        resp = self.client.delete(
            reverse(OrderCancelView.view_name, args=[order_1.id]))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        # two orders
        with self.assertRaises(Order.DoesNotExist):
            Order.objects.get(pk=order_1.id)

        master = Master.objects.get(pk=master.id)
        self.assertEqual(master.balance.future, 0)

    def test_cancel_order_too_late(self):
        master = Master.objects.get(first_name='VASYA')

        service = master.services.all()[0]
        # manually creating an order

        order_1, _ = make_order(client=self.client_object,
                                master=master,
                                service=service,
                                order_date=timezone.now(),
                                order_time=datetime.time(hour=11,
                                                         minute=00))

        frozen = freeze_time(timezone.now().replace(hour=9, minute=0))
        frozen.start()
        resp = self.client.delete(
            reverse(OrderCancelView.view_name, args=[order_1.id]))
        frozen.stop()

        # too late
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_cancel_someone_elses_order(self):
        master = Master.objects.get(first_name='VASYA')

        service = master.services.all()[0]
        # manually creating an order
        order_1, _ = make_order(client=self.client_object, master=master,
                                service=service,
                                order_time=datetime.time(hour=11, minute=00))

        token, _ = Token.objects.get_or_create(client=make_client())
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        resp = self.client.delete(
            reverse(OrderCancelView.view_name, args=[order_1.id]))

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
