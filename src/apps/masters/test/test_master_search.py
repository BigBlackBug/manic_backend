from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.masters import utils
from src.apps.masters.models import Master
from src.apps.masters.serializers import MasterListSerializer
from src.apps.masters.test import make_everything, make_token
from src.apps.masters.views import MasterListView


class MastersTestCase(APITestCase):
    def setUp(self):
        make_everything()
        self.token = make_token()
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def tearDown(self):
        self.token.user.delete()

    def test_serializer(self):
        master = Master.objects.get(first_name='VASYA')

        serializer = MasterListSerializer(instance=master)
        data = serializer.data
        # omit services
        self.assertEqual(data['first_name'], master.first_name)
        self.assertIn('avatar', data)
        self.assertEqual(data['id'], master.id)
        self.assertEqual(data['location']['lat'], master.location.lat)
        self.assertEqual(data['location']['lon'], master.location.lon)
        self.assertEqual(data['distance'], serializer.DISTANCE_NOT_AVAILABLE)

    def test_filtering_distance(self):
        url = f'{reverse(MasterListView.view_name)}?' \
              f'distance=200&' \
              f'coordinates=10.03,12.43'
        resp = self.client.get(url)
        print(resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 2)
        # ordered by distance
        self.assertGreater(resp.data[0]['distance'], resp.data[1]['distance'])

    def test_fail_no_coords(self):
        url = f'{reverse(MasterListView.view_name)}?' \
              f'distance=200'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filtering_time(self):
        url = f"{reverse(MasterListView.view_name)}?" \
              f"time_between=10:30,11:30&" \
              f"coordinates=10.03,12.43"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # both can do any of his services on any day in the given time
        self.assertEqual(len(resp.data), 2)

    def test_filtering_date(self):
        url = f"{reverse(MasterListView.view_name)}?" \
              f"date_between={utils.get_date(0)},{utils.get_date(7)}&" \
              f"coordinates=10.03,12.43"
        resp = self.client.get(url)
        print(resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # both do at least one service in the following week
        self.assertEqual(len(resp.data), 2)

    def test_filtering_service(self):
        master = Master.objects.get(first_name='VASYA')
        service = master.services.all()[0]

        url = f"{reverse(MasterListView.view_name)}?" \
              f"services={service.id}&" \
              f"coordinates=10.03,12.43"
        resp = self.client.get(url)
        # VASYA can do 'service' in the following two weeks
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['first_name'], 'VASYA')
