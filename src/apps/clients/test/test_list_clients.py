from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.authentication.models import Token, PhoneAuthUser
from src.apps.authentication.utils import Gender
from src.apps.clients.models import Client, Address
from src.apps.clients.views import ClientCreateView
from src.apps.core import utils
from src.apps.core.models import Location


class ClientListTestCase(APITestCase):
    def setUp(self):
        self.user = PhoneAuthUser.objects.create(phone='777')
        self.client_object = Client.objects.create(user=self.user, first_name='client',
                                                   avatar=utils.make_in_memory_image('supername'),
                                                   gender=Gender.MALE,
                                                   date_of_birth=timezone.now(),
                                                   address=Address.objects.create(
                                                       location=Location.objects.create(lat=10,
                                                                                        lon=10),
                                                       city='kazan', street_name='latstr',
                                                       building='4', floor=2, apt_number=79,
                                                       entrance=6, has_intercom=True))
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_create_client_existing_account(self):
        resp = self.client.post(reverse(ClientCreateView.view_name), data={
            'first_name': 'VASYA',
            'gender': Gender.MALE,
            'date_of_birth': utils.get_date(-100),
            'tip': 10,
            'address': {
                'location': {
                    'lat': 100,
                    'lon': 100,
                }, 'city': 'kazan', 'street_name': 'latstr',
                'building': '4', 'floor': 2,
                'apt_number': 79,
                'entrance': 6, 'has_intercom': True}
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_client(self):
        user = PhoneAuthUser.objects.create(phone='77777')
        # login with a new user
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        resp = self.client.post(reverse(ClientCreateView.view_name), data={
            'first_name': 'VASYA',
            'gender': Gender.MALE,
            'date_of_birth': utils.get_date(-100),
            'tip': 10,
            'address': {
                'location': {
                    'lat': 100,
                    'lon': 100,
                }, 'city': 'kazan', 'street_name': 'latstr',
                'building': '4', 'floor': 2,
                'apt_number': 79,
                'entrance': 6, 'has_intercom': True}
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        Client.objects.get(first_name='VASYA')
        # TODO assert that evertything is fine
        pass
