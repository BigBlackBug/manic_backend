from datetime import datetime

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.authentication.models import Token
from src.apps.masters.models import Master, Schedule, TimeSlot, Time
from src.apps.masters.views import CreateDeleteScheduleView
from src.utils.object_creation import make_master


class DeleteScheduleTestCase(APITestCase):
    def setUp(self):
        # make_everything()
        self.master_object = make_master('VASYA', 10)
        self.user = self.master_object.user
        token, _ = Token.objects.get_or_create(master=self.master_object)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_delete_time_slots(self):
        schedule = Schedule.objects.create(master=self.master_object,
                                           date='2017-11-20')
        TimeSlot.objects.create(time=Time.objects.create(hour=10, minute=30),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=00),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=30),
                                taken=False,
                                schedule=schedule),
        resp = self.client.patch(
            reverse(CreateDeleteScheduleView.view_name,
                    args=[self.master_object.id]), data={
                'date': '2017-11-20',
                'time_slots': '10:30,11:00'
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        master = Master.objects.get(first_name='VASYA')
        schedules = master.schedule.all()
        self.assertEqual(len(schedules), 1)
        schedule = schedules[0]

        self.assertEqual(schedule.date,
                         datetime.strptime('2017-11-20', '%Y-%m-%d').date())

        self.assertIsNone(schedule.get_slot('10:30'))
        self.assertIsNone(schedule.get_slot('11:00'))

    def test_delete_time_slots_and_schedule(self):
        schedule = Schedule.objects.create(master=self.master_object,
                                           date='2017-11-20')
        TimeSlot.objects.create(time=Time.objects.create(hour=10, minute=30),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=00),
                                taken=False,
                                schedule=schedule),
        resp = self.client.patch(
            reverse(CreateDeleteScheduleView.view_name,
                    args=[self.master_object.id]), data={
                'date': '2017-11-20',
                'time_slots': '10:30,11:00'
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        master = Master.objects.get(first_name='VASYA')
        schedules = master.schedule.all()
        # both timeslots are deleted -> the schedule is deleted
        self.assertEqual(len(schedules), 0)

    def test_delete_time_slots_range(self):
        schedule = Schedule.objects.create(master=self.master_object,
                                           date='2017-11-20')
        TimeSlot.objects.create(time=Time.objects.create(hour=10, minute=30),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=00),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=30),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=12, minute=0),
                                taken=False,
                                schedule=schedule),
        resp = self.client.patch(
            reverse(CreateDeleteScheduleView.view_name,
                    args=[self.master_object.id]), data={
                'date': '2017-11-20',
                'time_slots': '10:30-11:30'
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        master = Master.objects.get(first_name='VASYA')
        schedules = master.schedule.all()
        self.assertEqual(len(schedules), 1)
        schedule = schedules[0]

        self.assertEqual(schedule.date,
                         datetime.strptime('2017-11-20', '%Y-%m-%d').date())

        self.assertIsNone(schedule.get_slot('10:30'))
        self.assertIsNone(schedule.get_slot('11:00'))
        self.assertIsNone(schedule.get_slot('11:30'))

    def test_delete_time_slots_wrong_date(self):
        schedule = Schedule.objects.create(master=self.master_object,
                                           date='2017-11-20')
        TimeSlot.objects.create(time=Time.objects.create(hour=10, minute=30),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=00),
                                taken=False,
                                schedule=schedule),
        resp = self.client.patch(
            reverse(CreateDeleteScheduleView.view_name,
                    args=[self.master_object.id]), data={
                'date': '2017-11-21',
                'time_slots': '10:30,11:00'
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_time_slots_taken(self):
        schedule = Schedule.objects.create(master=self.master_object,
                                           date='2017-11-20')
        TimeSlot.objects.create(time=Time.objects.create(hour=10, minute=30),
                                taken=True,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=00),
                                taken=False,
                                schedule=schedule),
        TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=30),
                                taken=False,
                                schedule=schedule),
        resp = self.client.patch(
            reverse(CreateDeleteScheduleView.view_name,
                    args=[self.master_object.id]), data={
                'date': '2017-11-20',
                'time_slots': '10:30-11:30'
            }, format='json')
        self.assertEqual(resp.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)
