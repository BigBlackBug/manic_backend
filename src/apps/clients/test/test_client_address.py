from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.authentication.models import Token, PhoneAuthUser
from src.apps.authentication.utils import Gender
from src.apps.clients.models import Client, Address
from src.apps.clients.views import AddAddressView, AddressUpdateView
from src.apps.core import utils
from src.apps.core.models import Location
from src.apps.masters.test import make_client


class CreateClientTestCase(APITestCase):
    def setUp(self):
        self.user = PhoneAuthUser.objects.create(phone='777')
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_add_extra_address(self):
        client_object = make_client(self.user)
        resp = self.client.post(reverse(AddAddressView.view_name,
                                        args=[client_object.id]),
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
        new_client = Client.objects.create(user=self.user, first_name='client',
                                           avatar=utils.make_in_memory_image(
                                               'supername'),
                                           gender=Gender.MALE,
                                           date_of_birth=timezone.now())
        resp = self.client.post(reverse(AddAddressView.view_name,
                                        args=[new_client.id]), data={
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
        client_object = make_client(self.user)
        address = Address.objects.create(
            location=Location.objects.create(lat=10,
                                             lon=10),
            city='NSK', street_name='latstr',
            building='4', floor=2, apt_number=79,
            entrance=6, has_intercom=True, client=client_object,
            is_default=False)

        resp = self.client.patch(reverse(AddressUpdateView.view_name,
                                         args=[client_object.id, address.id]),
                                 data={
                                     'is_default': True
                                 },format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        client_object = Client.objects.first()
        self.assertEqual(len(client_object.addresses.all()), 2)
        self.assertEqual(client_object.home_address.city, 'NSK')

    def test_update_address(self):
        client_object = make_client(self.user)
        address = Address.objects.create(
            location=Location.objects.create(lat=10,
                                             lon=10),
            city='NSK', street_name='latstr',
            building='4', floor=2, apt_number=79,
            entrance=6, has_intercom=True, client=client_object,
            is_default=False)

        resp = self.client.patch(reverse(AddressUpdateView.view_name,
                                         args=[client_object.id, address.id]),
                                 data={
                                     'city': 'MOSCOW'
                                 },format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        client_object = Client.objects.first()
        self.assertEqual(len(client_object.addresses.all()), 2)
        self.assertEqual(client_object.addresses.get(pk=address.id).city,
                         'MOSCOW')

    def test_delete_address(self):
        client_object = make_client(self.user)
        resp = self.client.delete(reverse(AddressUpdateView.view_name,
                                          args=[client_object.id,
                                                client_object.home_address.id]))

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        client_object = Client.objects.first()
        self.assertEqual(len(client_object.addresses.all()), 0)
        self.assertEqual(client_object.home_address, None)
