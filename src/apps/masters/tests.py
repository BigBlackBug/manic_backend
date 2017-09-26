import json

from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.authentication.models import PhoneAuthUser, Token
from src.apps.categories.models import ServiceCategory, Service
from src.apps.core import utils
from .models import Master, Location, Schedule, TimeSlot
from .receivers import *
from .serializers import MasterListSerializer, MasterScheduleSerializer
from .utils import Gender
from .views import MasterListView, MasterDetailView, MasterScheduleView


class MastersTestCase(APITestCase):

    def setUp(self):
        # making an auth token
        self.user = PhoneAuthUser.objects.create(phone='777')
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        self.user2 = PhoneAuthUser.objects.create(phone='7777')

        self.category = ServiceCategory.objects.create(name='cat',
                                                       image=utils.make_in_memory_image('img'))

        self.service = Service.objects.create(category=self.category, name='d',
                                              description='d',
                                              cost=10,
                                              min_duration=10,
                                              max_duration=20)
        self.master = Master.objects.create(user=self.user, first_name='master',
                                            avatar=utils.make_in_memory_image('supername'),
                                            gender=Gender.MALE, date_of_birth=timezone.now(),
                                            location=Location.objects.create(lat=10, lon=11))
        self.master2 = Master.objects.create(user=self.user2,
                                             first_name='master2',
                                             avatar=utils.make_in_memory_image('supername'),
                                             gender=Gender.MALE, date_of_birth=timezone.now(),
                                             location=Location.objects.create(lat=10, lon=12))
        self.master2.save()

        self.master.save()
        self.master.services.add(self.service)

        schedule = Schedule.objects.create(master=self.master, date='2017-09-25')
        schedule.save()

        TimeSlot.objects.create(time=Time.objects.create(hour=10, minute=30),
                                taken=False, schedule=schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=12, minute=30),
                                taken=True, schedule=schedule)

    def tearDown(self):
        self.master.delete()
        self.master2.delete()

    def test_serializer(self):
        serializer = MasterListSerializer(instance=self.master)
        data = serializer.data
        # omit services
        self.assertEqual(data['first_name'], self.master.first_name)
        self.assertIn('avatar', data)
        self.assertEqual(data['id'], self.master.id)
        self.assertEqual(data['location']['lat'], self.master.location.lat)
        self.assertEqual(data['location']['lon'], self.master.location.lon)
        self.assertEqual(data['distance'], serializer.DISTANCE_NOT_AVAILABLE)

    def test_filtering_distance(self):
        url = "%s?distance=200&coordinates=10.03,12.43" % reverse(MasterListView.view_name)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)
        # ordered by distance
        self.assertGreater(resp.data[0]['distance'], resp.data[1]['distance'])

    def test_filtering_distance_fail_no_coords(self):
        url = "%s?distance=200" % reverse(MasterListView.view_name)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filtering_time(self):
        url = "%s?time_0=10:30&time_1=11:30&" % reverse(MasterListView.view_name)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['first_name'], self.master.first_name)

    def test_filtering_date(self):
        url = "%s?date_0=2017-09-24&date_1=2017-09-29" % reverse(MasterListView.view_name)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['first_name'], self.master.first_name)

    def test_filtering_service(self):
        url = "%s?service_in=%s" % (reverse(MasterListView.view_name), self.service.id)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['first_name'], self.master.first_name)

    def test_master_does_not_exist(self):
        resp = self.client.get(reverse(MasterDetailView.view_name, args=[10]))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_master_exists(self):
        resp = self.client.get(reverse(MasterDetailView.view_name, args=[1]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_master_schedule(self):
        resp = self.client.get(reverse(MasterScheduleView.view_name, args=[1]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        serializer = MasterScheduleSerializer(self.master)
        self.assertEqual(resp.data, serializer.data)
