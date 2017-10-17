import datetime

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from src.apps.authentication.models import PhoneAuthUser, Token
from src.apps.authentication.utils import Gender
from src.apps.categories.models import ServiceCategory
from src.apps.clients.models import Client, Address
from src.apps.core import utils
from src.apps.core.models import Location
from src.apps.masters.models import Master, TimeSlot, Time, Schedule
from src.apps.masters.test import make_everything, make_master
from src.apps.orders.models import Order
from src.apps.orders.views import OrderCreateView


class OrderCreateTestCase(TestCase):
    def setUp(self):
        make_everything()
        self.user = PhoneAuthUser.objects.create(phone='777')
        self.client_object = Client.objects.create(user=self.user, first_name='client',
                                                   avatar=utils.make_in_memory_image('supername'),
                                                   gender=Gender.MALE,
                                                   date_of_birth=timezone.now(),
                                                   address=Address.objects.create(
                                                       location=Location.objects.create(lat=10,
                                                                                        lon=10),
                                                       city='kazan', street_name='latstr',
                                                       building='4', floor=2, apt_number=79,
                                                       entrance=6, has_intercom=True))
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_create_order__one_master_one_service(self):
        master = Master.objects.get(first_name='VASYA')
        service = master.services.first()
        # one service 2+1 slots
        resp = self.client.post(reverse(OrderCreateView.view_name), data={
            'date': timezone.now().strftime('%Y-%m-%d'),
            'time': '11:00',
            'order_items': [{
                'master_id': master.id,
                'service_ids': [service.id]
            }, ]
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        master = Master.objects.get(first_name='VASYA')
        schedule = master.schedule.get(date=timezone.now().strftime('%Y-%m-%d'))

        # assert timeslots are correctly set
        slots = schedule.time_slots.filter(time__value__in=['11:00', '11:30', '12:00'], taken=True)
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

    def test_create_order__one_master_many_services(self):
        master = Master.objects.get(first_name='VASYA')
        schedule = master.get_schedule(timezone.now())
        TimeSlot.objects.create(time=Time.objects.create(hour=12, minute=30),
                                taken=False, schedule=schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=13, minute=00),
                                taken=False, schedule=schedule)
        services = master.services.all()
        # two services, 5 slots, no+1
        resp = self.client.post(reverse(OrderCreateView.view_name), data={
            'date': timezone.now().strftime('%Y-%m-%d'),
            'time': '11:00',
            'order_items': [{
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
                                                            '13:00'], taken=True)
        self.assertEqual(len(slots), 5)
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
        self.assertEqual(order_item.master, master)
        self.assertEqual(order_item.service, services[0])
        self.assertEqual(order_item_1.master, master)
        self.assertEqual(order_item_1.service, services[1])

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
        resp = self.client.post(reverse(OrderCreateView.view_name), data={
            'date': timezone.now().strftime('%Y-%m-%d'),
            'time': '11:00',
            'order_items': [{
                'master_id': vasya.id,
                'service_ids': [vasya.services.first().id]
            }, {
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
                                                            '12:00'], taken=True)
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