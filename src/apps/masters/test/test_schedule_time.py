import datetime

from django.test import TestCase
from django.utils import timezone

from src.apps.masters.models import TimeSlot, Schedule, Time
from src.utils.object_creation import make_master


class ScheduleTestCase(TestCase):
    def test_schedule_assign_time(self):
        master = make_master('master', 100)
        schedule = Schedule.objects.create(master=master, date=timezone.now())
        TimeSlot.objects.create(time=Time.objects.create(hour=10, minute=30),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=00),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=30),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=12, minute=00),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=12, minute=30),
                                taken=False,
                                schedule=schedule),

        next_time = schedule.assign_time(
            time_=datetime.time(hour=10, minute=30),
            number_of_slots=3)

        self.assertEqual(datetime.time(hour=12, minute=00), next_time)
        slots = schedule.time_slots.filter(
            time__value__in=['10:30', '11:00', '11:30'],
            taken=True)
        self.assertEqual(len(slots), 3)

    def test_schedule_assign_time_end_of_day(self):
        master = make_master('master', 100)
        schedule = Schedule.objects.create(master=master, date=timezone.now())
        TimeSlot.objects.create(time=Time.objects.create(hour=10, minute=30),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=00),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=30),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=12, minute=00),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=12, minute=30),
                                taken=False,
                                schedule=schedule),

        next_time = schedule.assign_time(
            time_=datetime.time(hour=12, minute=00),
            number_of_slots=2)

        self.assertIsNone(next_time)
        slots = schedule.time_slots.filter(time__value__in=['12:00', '12:30'],
                                           taken=True)
        self.assertEqual(len(slots), 2)

    def test_schedule_assign_time_time_not_found(self):
        master = make_master('master', 100)
        schedule = Schedule.objects.create(master=master, date=timezone.now())
        TimeSlot.objects.create(time=Time.objects.create(hour=10, minute=30),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=00),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=30),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=12, minute=00),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=12, minute=30),
                                taken=False,
                                schedule=schedule),

        with self.assertRaises(ValueError):
            schedule.assign_time(time_=datetime.time(hour=21, minute=10),
                                 number_of_slots=3)
