import datetime
from datetime import timedelta as delta

from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.authentication.models import PhoneAuthUser, Token
from src.apps.core import utils
from src.apps.masters.models import Master
from src.apps.masters.serializers import SimpleMasterSerializer
from src.apps.masters.views import MasterListCreateView
from src.utils.object_creation import make_everything, make_client, make_order


class MasterListTestCase(APITestCase):
    def setUp(self):
        make_everything()
        self.user = PhoneAuthUser.objects.create(phone='777')
        self.client_object = make_client(self.user)
        token, _ = Token.objects.get_or_create(client=self.client_object)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_serializer(self):
        master = Master.objects.get(first_name='VASYA')

        serializer = SimpleMasterSerializer(instance=master)
        data = serializer.data
        # omit services
        self.assertEqual(data['first_name'], master.first_name)
        self.assertIn('avatar', data)
        self.assertEqual(data['id'], master.id)
        self.assertEqual(data['location']['lat'], master.location.lat)
        self.assertEqual(data['location']['lon'], master.location.lon)
        self.assertEqual(data['distance'], serializer.DISTANCE_NOT_AVAILABLE)

    def test_filtering_distance(self):
        url = f'{reverse(MasterListCreateView.view_name)}?' \
              f'distance=200&' \
              f'coordinates=10.03,12.43'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # no favorites in this test
        favorites = resp.data['favorites']
        self.assertEqual(len(favorites), 0)
        others = resp.data['others']
        # both do at least one service in the following week
        self.assertEqual(len(others), 2)

        # ordered by distance
        self.assertLess(others[0]['distance'], others[1]['distance'])

    def test_fail_no_coords(self):
        url = f'{reverse(MasterListCreateView.view_name)}?' \
              f'distance=200'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filtering_time(self):
        url = f"{reverse(MasterListCreateView.view_name)}?" \
              f"time_range=10:30,11:30&" \
              f"coordinates=10.03,12.43"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # only PETYA can do at least one of his services on any day in the given time
        # no favorites in this test
        favorites = resp.data['favorites']
        self.assertEqual(len(favorites), 0)
        others = resp.data['others']
        # both do at least one service in the following week
        self.assertEqual(len(others), 1)
        self.assertEqual(others[0]['first_name'], 'PETYA')

    def test_filtering_date(self):
        url = f"{reverse(MasterListCreateView.view_name)}?" \
              f"date_range={utils.get_date(0)},{utils.get_date(7)}&" \
              f"coordinates=10.03,12.43"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # no favorites in this test
        favorites = resp.data['favorites']
        self.assertEqual(len(favorites), 0)
        others = resp.data['others']
        # both do at least one service in the following week
        self.assertEqual(len(others), 2)

    def test_filtering_date_favorites(self):
        # manually creating an order with vasya
        vasya = Master.objects.get(first_name='VASYA')
        make_order(client=self.client_object, master=vasya,
                   service=vasya.services.all()[0],
                   order_date=timezone.now() + delta(days=1),
                   order_time=datetime.time(hour=10, minute=30))

        url = f"{reverse(MasterListCreateView.view_name)}?" \
              f"date_range={utils.get_date(1)},{utils.get_date(8)}&" \
              f"coordinates=10.03,12.43"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # VASYA is favorite
        favorites = resp.data['favorites']
        self.assertEqual(len(favorites), 1)
        self.assertEqual(favorites[0]['first_name'], 'VASYA')

        others = resp.data['others']
        # PETYA is not
        # both do at least one service in the following week
        self.assertEqual(len(others), 1)
        self.assertEqual(others[0]['first_name'], 'PETYA')

    def test_filtering_date_one_day(self):
        url = f"{reverse(MasterListCreateView.view_name)}?" \
              f"date_range={utils.get_date(1)},{utils.get_date(1)}&" \
              f"coordinates=10.03,12.43"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # only VASYA is available
        # no favorites in this test
        favorites = resp.data['favorites']
        self.assertEqual(len(favorites), 0)
        others = resp.data['others']
        self.assertEqual(len(others), 1)

    def test_filtering_service(self):
        master = Master.objects.get(first_name='VASYA')
        service = master.services.all()[0]

        url = f"{reverse(MasterListCreateView.view_name)}?" \
              f"services={service.id}&" \
              f"coordinates=10.03,12.43"
        resp = self.client.get(url)
        # VASYA can do 'service' in the following two weeks
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # no favorites in this test
        favorites = resp.data['favorites']
        self.assertEqual(len(favorites), 0)
        others = resp.data['others']
        # both do at least one service in the following week
        self.assertEqual(len(others), 1)

        self.assertEqual(others[0]['first_name'], 'VASYA')
