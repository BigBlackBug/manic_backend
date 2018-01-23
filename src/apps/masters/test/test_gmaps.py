import datetime
from unittest import mock

from django.utils import timezone
from rest_framework.test import APITestCase

from src.apps.core.exceptions import ApplicationError
from src.apps.core.models import Location
from src.apps.masters import gmaps_utils
from src.apps.masters.models import Schedule, TimeSlot, Time
from src.apps.orders.models import OrderItem, Order
from src.utils.object_creation import make_master, make_category, make_client


class GmapsTestCase(APITestCase):
    def setUp(self):
        self.vasya = make_master('VASYA', 120)
        self.category = make_category('CATEGORY')
        for service in self.category.services.all():
            self.vasya.services.add(service)
        self.vasya.save()

        self.schedule = Schedule.objects.create(master=self.vasya,
                                                date=timezone.now())
        self.schedule.save()

    def test_free_previous_slot(self):
        TimeSlot.objects.create(time=Time.objects.create(hour=10, minute=30),
                                taken=False, schedule=self.schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=00),
                                taken=False, schedule=self.schedule)
        location = Location.objects.create(lat=10, lon=120)

        self.assertTrue(gmaps_utils.can_reach(self.schedule, location,
                                              datetime.time(hour=11,
                                                            minute=00)))

    @mock.patch.object(gmaps_utils, '_calculate_eta')
    def test_can_reach(self, _calculate_eta):
        slot = TimeSlot.objects.create(
            time=Time.objects.create(hour=10, minute=30),
            taken=True, schedule=self.schedule)
        order = Order.objects.create(client=make_client(), date=timezone.now(),
                                     time=timezone.now().time())
        slot.order_item = OrderItem.objects.create(
            service=self.vasya.services.first(),
            master=self.vasya,
            order=order,
            locked=False)
        slot.save()
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=00),
                                taken=False, schedule=self.schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=30),
                                taken=False, schedule=self.schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=12, minute=00),
                                taken=False, schedule=self.schedule)
        location = Location.objects.create(lat=10, lon=120)

        _calculate_eta.return_value = 10
        self.assertTrue(gmaps_utils.can_reach(self.schedule, location,
                                              datetime.time(hour=11,
                                                            minute=00)))

    @mock.patch.object(gmaps_utils, '_calculate_eta')
    def test_cant_reach(self, _calculate_eta):
        slot = TimeSlot.objects.create(
            time=Time.objects.create(hour=10, minute=30),
            taken=True, schedule=self.schedule)
        order = Order.objects.create(client=make_client(), date=timezone.now(),
                                     time=timezone.now().time())
        slot.order_item = OrderItem.objects.create(
            service=self.vasya.services.first(),
            master=self.vasya,
            order=order,
            locked=False)
        slot.save()
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=00),
                                taken=False, schedule=self.schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=30),
                                taken=False, schedule=self.schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=12, minute=00),
                                taken=False, schedule=self.schedule)
        location = Location.objects.create(lat=10, lon=120)

        _calculate_eta.return_value = 10000
        self.assertFalse(gmaps_utils.can_reach(self.schedule, location,
                                               datetime.time(hour=11,
                                                             minute=00)))

    @mock.patch.object(gmaps_utils, '_calculate_eta')
    def test_gmaps_api_unavailable(self, _calculate_eta):
        slot = TimeSlot.objects.create(
            time=Time.objects.create(hour=10, minute=30),
            taken=True, schedule=self.schedule)
        order = Order.objects.create(client=make_client(), date=timezone.now(),
                                     time=timezone.now().time())
        slot.order_item = OrderItem.objects.create(
            service=self.vasya.services.first(),
            master=self.vasya,
            order=order,
            locked=False)
        slot.save()
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=00),
                                taken=False, schedule=self.schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=30),
                                taken=False, schedule=self.schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=12, minute=00),
                                taken=False, schedule=self.schedule)
        location = Location.objects.create(lat=10, lon=120)

        _calculate_eta.side_effect = ApplicationError('HEY')
        with self.assertRaises(ApplicationError):
            gmaps_utils.can_reach(self.schedule, location,
                                  datetime.time(hour=11, minute=00))
