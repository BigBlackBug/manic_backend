from datetime import datetime

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.authentication.models import Token
from src.apps.categories.models import Service
from src.apps.masters.models import Master
from src.apps.masters.test import make_master
from src.apps.masters.views import MasterDetailUpdateView


class UpdateMasterTestCase(APITestCase):
    def setUp(self):
        self.master_object = make_master('NAME', 10)
        token, _ = Token.objects.get_or_create(master=self.master_object)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_update_name(self):
        master_id = self.master_object.id
        resp = self.client.patch(
            reverse(MasterDetailUpdateView.view_name, args=[master_id]), data={
                'first_name': 'Anna'
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.master_object = Master.objects.get(pk=master_id)
        # name changed
        self.assertEqual(self.master_object.first_name, 'Anna')

    def test_update_location(self):
        master_id = self.master_object.id
        resp = self.client.patch(
            reverse(MasterDetailUpdateView.view_name, args=[master_id]), data={
                'location': {'lat': 10, 'lon': 12}
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.master_object = Master.objects.get(pk=master_id)
        # location changed
        self.assertIsNotNone(self.master_object.location)
        self.assertEqual(self.master_object.location.lat, 10)
        self.assertEqual(self.master_object.location.lon, 12)

    def test_update_services(self):
        master_id = self.master_object.id
        self.assertEqual(len(self.master_object.services.all()), 0)

        new_services = [service.id for service in Service.objects.all()]
        resp = self.client.patch(
            reverse(MasterDetailUpdateView.view_name, args=[master_id]), data={
                'services': new_services
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.master_object = Master.objects.get(pk=master_id)
        # apt number changed
        self.assertEqual(len(self.master_object.services.all()),
                         len(new_services))

    def test_update_multiple(self):
        master_id = self.master_object.id
        resp = self.client.patch(
            reverse(MasterDetailUpdateView.view_name, args=[master_id]), data={
                'date_of_birth': '1999-10-20',
                'gender': 'F'
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.master_object = Master.objects.get(pk=master_id)
        # apt number changed
        self.assertEqual(self.master_object.date_of_birth,
                         datetime.strptime('1999-10-20', '%Y-%m-%d').date())
        self.assertEqual(self.master_object.gender, 'F')
