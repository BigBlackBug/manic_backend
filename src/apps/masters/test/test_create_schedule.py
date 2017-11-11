from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.authentication.models import Token
from src.apps.masters.models import Master, Schedule, TimeSlot, Time
from src.apps.masters.test import make_master
from src.apps.masters.utils import get_default_date_range
from src.apps.masters.views import CreateScheduleView


class CreateScheduleTestCase(APITestCase):
    def setUp(self):
        # make_everything()
        self.master_object = make_master('VASYA', 10)
        self.user = self.master_object.user
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_create_new_schedule(self):
        master = Master.objects.get(first_name='VASYA')
        resp = self.client.post(
            reverse(CreateScheduleView.view_name, args=[master.id]), data={
                'date': '2017-11-20',
                'time_slots': '13:00, 13:00-15:00'
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        master = Master.objects.get(first_name='VASYA')
        schedules = master.schedule.all()
        self.assertEqual(len(schedules), 1)
        schedule = schedules[0]
        self.assertEqual(schedule.date,
                         datetime.strptime('2017-11-20', '%Y-%m-%d').date())

        result_times = ['13:00', '13:30', '14:00', '14:30']
        self.assertEqual(len(schedule.time_slots.all()), len(result_times))

        for time_slot in schedule.time_slots.all():
            self.assertIn(str(time_slot.time), result_times)

    def test_fail_create_future_date(self):
        master = Master.objects.get(first_name='VASYA')
        resp = self.client.post(
            reverse(CreateScheduleView.view_name, args=[master.id]), data={
                'date': get_default_date_range(15)[1].strftime(
                    '%Y-%m-%d'),
                'time_slots': '13:00, 13:00-15:00'
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_slots_to_existing_schedule(self):
        schedule = Schedule.objects.create(master=self.master_object,
                                           date=timezone.now())
        TimeSlot.objects.create(time=Time.objects.create(hour=10, minute=30),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=00),
                                taken=False,
                                schedule=schedule),

        resp = self.client.post(
            reverse(CreateScheduleView.view_name, args=[self.master_object.id]),
            data={
                'date': get_default_date_range(3)[1].strftime(
                    '%Y-%m-%d'),
                'time_slots': '10:30,11:00,11:30'
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        master = Master.objects.get(first_name='VASYA')
        schedules = master.schedule.all()

        self.assertEqual(len(schedules), 2)
        schedule = schedules[0]
        self.assertEqual(schedule.date,
                         datetime.strptime('2017-11-20', '%Y-%m-%d').date())

        result_times = ['10:30', '11:00', '11:30']
        self.assertEqual(len(schedule.time_slots.all()), len(result_times))

        for time_slot in schedule.time_slots.all():
            self.assertIn(str(time_slot.time), result_times)
