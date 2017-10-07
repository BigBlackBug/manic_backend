import datetime

from django.test import TestCase

from src.apps.categories.models import Service, ServiceCategory
from src.apps.core import utils
from src.apps.masters import time_slot_utils
from src.apps.masters.models import TimeSlot, Time
from src.apps.masters.test import _make_time


class TimeUtilsTestCase(TestCase):
    def setUp(self):
        self.category = ServiceCategory.objects.create(name='category',
                                                       image=utils.make_in_memory_image('img'))

        self.service = Service.objects.create(category=self.category, name='Service обычный',
                                              description='d',
                                              cost=10,
                                              min_duration=30,
                                              max_duration=60)

    def test_find_avaiable_slots(self):
        time_slots = [
            TimeSlot(time=_make_time(10, 30), taken=False),
            TimeSlot(time=_make_time(11, 00), taken=False),
            TimeSlot(time=_make_time(11, 30), taken=False),
            TimeSlot(time=_make_time(12, 00), taken=False),
            TimeSlot(time=_make_time(12, 30), taken=False),
        ]
        # TimeSlot.objects.bulk_create(time)
        # max - 60 - 2+1 slots
        result = time_slot_utils.find_available_starting_slots(self.service, time_slots)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0].value, datetime.time(hour=10, minute=30))
        self.assertEqual(result[1].value, datetime.time(hour=11, minute=0))
        self.assertEqual(result[2].value, datetime.time(hour=11, minute=30))
        self.assertEqual(result[3].value, datetime.time(hour=12, minute=0))

    def test_find_avaiable_slots_no_slots(self):
        time_slots = [
            TimeSlot(time=_make_time(10, 30), taken=False),
            TimeSlot(time=_make_time(11, 00), taken=True),
            TimeSlot(time=_make_time(11, 30), taken=False),
            TimeSlot(time=_make_time(12, 00), taken=True),
            TimeSlot(time=_make_time(12, 30), taken=False),
        ]
        # TimeSlot.objects.bulk_create(time)
        # max - 60 - 2+1 slots
        result = time_slot_utils.find_available_starting_slots(self.service, time_slots)
        self.assertEqual(len(result), 0)

    def test_find_avaiable_slots_end_of_day_slot(self):
        time_slots = [
            TimeSlot(time=_make_time(10, 30), taken=True),
            TimeSlot(time=_make_time(11, 00), taken=True),
            TimeSlot(time=_make_time(11, 30), taken=True),
            TimeSlot(time=_make_time(12, 00), taken=False),
            TimeSlot(time=_make_time(12, 30), taken=False),
        ]
        # TimeSlot.objects.bulk_create(time)
        # max - 60 - 2+1 slots
        result = time_slot_utils.find_available_starting_slots(self.service, time_slots)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].value, datetime.time(hour=12, minute=0))

    def test_find_avaiable_slots_mid_day_slot(self):
        time_slots = [
            TimeSlot(time=_make_time(10, 30), taken=True),
            TimeSlot(time=_make_time(11, 00), taken=False),
            TimeSlot(time=_make_time(11, 30), taken=False),
            TimeSlot(time=_make_time(12, 00), taken=False),
            TimeSlot(time=_make_time(12, 30), taken=True),
        ]
        # TimeSlot.objects.bulk_create(time)
        # max - 60 - 2+1 slots
        result = time_slot_utils.find_available_starting_slots(self.service, time_slots)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].value, datetime.time(hour=11, minute=0))


class ScheduleFitTestCase(TestCase):
    def setUp(self):
        self.category = ServiceCategory.objects.create(name='category',
                                                       image=utils.make_in_memory_image('img'))

        self.service = Service.objects.create(category=self.category, name='Service обычный',
                                              description='d',
                                              cost=10,
                                              min_duration=30,
                                              max_duration=60)

    def test_fits(self):
        time_slots = [
            TimeSlot(time=_make_time(10, 30), taken=False),
            TimeSlot(time=_make_time(11, 00), taken=False),
            TimeSlot(time=_make_time(11, 30), taken=False),
            TimeSlot(time=_make_time(12, 00), taken=False),
            TimeSlot(time=_make_time(12, 30), taken=False),
        ]
        # max - 60 - 2+1 slots
        result = time_slot_utils.service_fits_into_slots(self.service, time_slots,
                                                         datetime.time(hour=10, minute=0),
                                                         datetime.time(hour=12, minute=0))
        self.assertTrue(result)

    def test_no_fit(self):
        time_slots = [
            TimeSlot(time=_make_time(10, 30), taken=False),
            TimeSlot(time=_make_time(11, 00), taken=True),
            TimeSlot(time=_make_time(11, 30), taken=False),
            TimeSlot(time=_make_time(12, 00), taken=False),
            TimeSlot(time=_make_time(12, 30), taken=True),
        ]
        # max - 60 - 2+1 slots
        result = time_slot_utils.service_fits_into_slots(self.service, time_slots,
                                                         datetime.time(hour=10, minute=0),
                                                         datetime.time(hour=16, minute=0))
        self.assertFalse(result)

    def test_fits_end_of_day(self):
        time_slots = [
            TimeSlot(time=_make_time(10, 30), taken=False),
            TimeSlot(time=_make_time(11, 00), taken=False),
            TimeSlot(time=_make_time(11, 30), taken=True),
            TimeSlot(time=_make_time(12, 00), taken=False),
            TimeSlot(time=_make_time(12, 30), taken=False),
        ]
        # max - 60 - 2+1 slots
        result = time_slot_utils.service_fits_into_slots(self.service, time_slots,
                                                         datetime.time(hour=12, minute=0),
                                                         datetime.time(hour=13, minute=0))
        self.assertTrue(result)

    def test_no_fit_filter(self):
        time_slots = [
            TimeSlot(time=_make_time(10, 30), taken=True),
            TimeSlot(time=_make_time(11, 00), taken=False),
            TimeSlot(time=_make_time(11, 30), taken=False),
            TimeSlot(time=_make_time(12, 00), taken=False),
            TimeSlot(time=_make_time(12, 30), taken=False),
        ]
        # max - 60 - 2+1 slots
        result = time_slot_utils.service_fits_into_slots(self.service, time_slots,
                                                         datetime.time(hour=10, minute=0),
                                                         datetime.time(hour=11, minute=30))
        self.assertFalse(result)
