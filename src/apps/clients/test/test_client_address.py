from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.authentication.models import Token, PhoneAuthUser
from src.apps.clients.models import Client, Address
from src.apps.clients.views import AddAddressView, AddressUpdateView
from src.apps.core.models import Location
from src.utils.object_creation import make_client


class ClientAddressTestCase(APITestCase):
    def setUp(self):
        self.user = PhoneAuthUser.objects.create(phone='777')
        self.client_object = make_client(self.user)
        token, _ = Token.objects.get_or_create(client=self.client_object)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_add_extra_address(self):
        resp = self.client.post(reverse(AddAddressView.view_name,
                                        args=[self.client_object.id]),
                                data={
                                    'location': {
                                        'lat': 100,
                                        'lon': 100,
                                    }, 'city': 'kazan', 'street_name': 'latstr',
                                    'building': '4', 'floor': 2,
                                    'apt_number': 79,
                                    'entrance': 6, 'has_intercom': True
                                }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_client_object = Client.objects.first()
        self.assertEqual(len(new_client_object.addresses.all()), 2)

    def test_add_first_address(self):
        self.client_object.addresses.clear()
        resp = self.client.post(reverse(AddAddressView.view_name,
                                        args=[self.client_object.id]), data={
            'location': {
                'lat': 100,
                'lon': 100,
            }, 'city': 'kazan', 'street_name': 'latstr',
            'building': '4', 'floor': 2,
            'apt_number': 79,
            'entrance': 6, 'has_intercom': True
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_client_object = Client.objects.first()
        self.assertEqual(len(new_client_object.addresses.all()), 1)
        # and other fields too
        self.assertEqual(new_client_object.home_address.city, 'kazan')

    def test_set_home_address(self):
        address = Address.objects.create(
            location=Location.objects.create(lat=10,
                                             lon=10),
            city='NSK', street_name='latstr',
            building='4', floor=2, apt_number=79,
            entrance=6, has_intercom=True, client=self.client_object,
            is_default=False)

        resp = self.client.patch(reverse(AddressUpdateView.view_name,
                                         args=[self.client_object.id,
                                               address.id]),
                                 data={
                                     'is_default': True
                                 }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        client_object = Client.objects.first()
        self.assertEqual(len(client_object.addresses.all()), 2)
        self.assertEqual(len(client_object.addresses.filter(
            is_default=True)), 1)
        self.assertEqual(client_object.home_address.city, 'NSK')

    def test_update_address(self):
        address = Address.objects.create(
            location=Location.objects.create(lat=10,
                                             lon=10),
            city='NSK', street_name='latstr',
            building='4', floor=2, apt_number=79,
            entrance=6, has_intercom=True, client=self.client_object,
            is_default=False)

        resp = self.client.patch(reverse(AddressUpdateView.view_name,
                                         args=[self.client_object.id,
                                               address.id]),
                                 data={
                                     'city': 'MOSCOW',
                                 }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        client_object = Client.objects.first()
        self.assertEqual(len(client_object.addresses.all()), 2)
        self.assertEqual(client_object.addresses.get(pk=address.id).city,
                         'MOSCOW')

    def test_delete_address(self):
        resp = self.client.delete(reverse(AddressUpdateView.view_name,
                                          args=[self.client_object.id,
                                                self.client_object.home_address.id]))

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        client_object = Client.objects.first()
        self.assertEqual(len(client_object.addresses.all()), 0)
        self.assertEqual(client_object.home_address, None)
