import datetime

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from src.apps.authentication.models import PhoneAuthUser, Token
from src.apps.categories.models import ServiceCategory
from src.apps.masters.models import Master, TimeSlot, Time, Schedule
from src.apps.orders.models import Order
from src.apps.orders.views import OrderListCreateView
from src.utils.object_creation import make_everything, make_master, make_client


class OrderCreateTestCase(TestCase):
    def setUp(self):
        make_everything()
        self.user = PhoneAuthUser.objects.create(phone='777')
        self.client_object = make_client(self.user)
        token, _ = Token.objects.get_or_create(client=self.client_object)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_create_order__one_master_one_service_card(self):
        master = Master.objects.get(first_name='VASYA')
        service = master.services.first()
        # one service 2+1 slots
        resp = self.client.post(reverse(OrderListCreateView.view_name), data={
            'date': timezone.now().strftime('%Y-%m-%d'),
            'payment_type': 'CARD',
            'time': '11:00',
            'order_items': [{
                'locked': False,
                'master_id': master.id,
                'service_ids': [service.id]
            }, ]
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        master = Master.objects.get(first_name='VASYA')
        schedule = master.schedule.get(date=timezone.now().strftime('%Y-%m-%d'))

        # assert timeslots are correctly set
        slots = schedule.time_slots.filter(
            time__value__in=['11:00', '11:30', '12:00'], taken=True)
        self.assertEqual(len(slots), 3)

        # assert order is created
        orders = Order.objects.all()
        self.assertTrue(len(orders), 1)
        order = orders[0]
        self.assertEqual(order.client, self.client_object)
        self.assertEqual(order.date, timezone.now().date())
        self.assertEqual(order.time, datetime.time(hour=11, minute=0))
        self.assertEqual(len(order.order_items.all()), 1)
        order_item = order.order_items.all()[0]

        # assert order_items are created
        self.assertEqual(order_item.master, master)
        self.assertEqual(order_item.service, service)

        # assert future balance is correct
        self.assertEqual(master.balance.future,
                         service.masters_share(
                             self.client_object.tip_multiplier()))

    def test_create_order__one_master_one_service_cash(self):
        master = Master.objects.get(first_name='VASYA')
        service = master.services.first()
        # one service 2+1 slots
        resp = self.client.post(reverse(OrderListCreateView.view_name), data={
            'date': timezone.now().strftime('%Y-%m-%d'),
            'payment_type': 'CASH',
            'time': '11:00',
            'order_items': [{
                'locked': False,
                'master_id': master.id,
                'service_ids': [service.id]
            }, ]
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        master = Master.objects.get(first_name='VASYA')
        schedule = master.schedule.get(date=timezone.now().strftime('%Y-%m-%d'))

        # assert timeslots are correctly set
        slots = schedule.time_slots.filter(
            time__value__in=['11:00', '11:30', '12:00'], taken=True)
        self.assertEqual(len(slots), 3)

        # assert order is created
        orders = Order.objects.all()
        self.assertTrue(len(orders), 1)
        order = orders[0]
        self.assertEqual(order.client, self.client_object)
        self.assertEqual(order.date, timezone.now().date())
        self.assertEqual(order.time, datetime.time(hour=11, minute=0))
        self.assertEqual(len(order.order_items.all()), 1)
        order_item = order.order_items.all()[0]

        # assert order_items are created
        self.assertEqual(order_item.master, master)
        self.assertEqual(order_item.service, service)

        # assert future balance is correct
        self.assertEqual(master.balance.future,
                         service.masters_share(
                             self.client_object.tip_multiplier()))
        # assert debt is correct
        self.assertEqual(master.balance.debt, service.service_share())

    def test_create_order__one_master_many_services(self):
        master = Master.objects.get(first_name='VASYA')
        schedule = master.get_schedule(timezone.now())
        TimeSlot.objects.create(time=Time.objects.create(hour=12, minute=30),
                                taken=False, schedule=schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=13, minute=00),
                                taken=False, schedule=schedule)
        services = master.services.all()
        # two services, 5 slots, no+1
        resp = self.client.post(reverse(OrderListCreateView.view_name), data={
            'date': timezone.now().strftime('%Y-%m-%d'),
            'payment_type': 'CARD',
            'time': '11:00',
            'order_items': [{
                'locked': False,
                'master_id': master.id,
                'service_ids': [service.id for service in services]
            }, ]
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        master = Master.objects.get(first_name='VASYA')
        schedule = master.schedule.get(date=timezone.now().strftime('%Y-%m-%d'))
        # assert timeslots are correctly set
        slots = schedule.time_slots.filter(time__value__in=['11:00', '11:30',
                                                            '12:00', '12:30',
                                                            '13:00'],
                                           taken=True)
        self.assertEqual(len(slots), 5)
        # assert order is created
        orders = Order.objects.all()
        self.assertTrue(len(orders), 1)
        order = orders[0]
        self.assertEqual(order.client, self.client_object)
        self.assertEqual(order.date, timezone.now().date())
        self.assertEqual(order.time, datetime.time(hour=11, minute=0))
        self.assertEqual(len(order.order_items.all()), 2)

        # assert future balance is correct
        self.assertEqual(master.balance.future,
                         sum(map(lambda s: int(
                             s.masters_share(
                                 self.client_object.tip_multiplier())),
                                 services)))

    def test_create_order__composite_4hands(self):
        vasya = Master.objects.get(first_name='VASYA')
        sanya = make_master("SANYA", 12.0)

        feet = ServiceCategory.objects.get(name="Педикюр")

        for service in feet.services.all():
            sanya.services.add(service)
        sanya.save()

        schedule = Schedule.objects.create(master=sanya, date=timezone.now())
        schedule.save()

        TimeSlot.objects.create(time=Time.objects.create(hour=10, minute=30),
                                taken=True, schedule=schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=00),
                                taken=False, schedule=schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=30),
                                taken=False, schedule=schedule)

        # two services, 2+1 for vasya, 2 for sanya
        resp = self.client.post(reverse(OrderListCreateView.view_name), data={
            'date': timezone.now().strftime('%Y-%m-%d'),
            'payment_type': 'CARD',
            'time': '11:00',
            'order_items': [{
                'locked': False,
                'master_id': vasya.id,
                'service_ids': [vasya.services.first().id]
            }, {
                'locked': False,
                'master_id': sanya.id,
                'service_ids': [sanya.services.first().id]
            }],
            'special': {
                'type': 'composite'
            }
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        vasya = Master.objects.get(first_name='VASYA')
        schedule = vasya.schedule.get(date=timezone.now().strftime('%Y-%m-%d'))
        # assert timeslots are correctly set
        slots = schedule.time_slots.filter(time__value__in=['11:00', '11:30',
                                                            '12:00'],
                                           taken=True)
        self.assertEqual(len(slots), 3)

        sanya = Master.objects.get(first_name='SANYA')
        schedule = sanya.schedule.get(date=timezone.now().strftime('%Y-%m-%d'))
        # assert timeslots are correctly set
        slots = schedule.time_slots.filter(time__value__in=['11:00', '11:30'],
                                           taken=True)
        self.assertEqual(len(slots), 2)

        # assert order is created
        orders = Order.objects.all()
        self.assertTrue(len(orders), 1)

        order = orders[0]
        self.assertEqual(order.client, self.client_object)
        self.assertEqual(order.date, timezone.now().date())
        self.assertEqual(order.time, datetime.time(hour=11, minute=0))
        self.assertEqual(len(order.order_items.all()), 2)
        order_item = order.order_items.all()[0]
        order_item_1 = order.order_items.all()[1]

        # assert order_items are created
        self.assertEqual(order_item.master, vasya)
        self.assertEqual(order_item.service, vasya.services.first())
        self.assertEqual(order_item_1.master, sanya)
        self.assertEqual(order_item_1.service, sanya.services.first())

        # assert future balance is correct
        self.assertEqual(vasya.balance.future,
                         vasya.services.first().masters_share(
                             self.client_object.tip_multiplier()))
        self.assertEqual(sanya.balance.future,
                         sanya.services.first().masters_share(
                             self.client_object.tip_multiplier()))
