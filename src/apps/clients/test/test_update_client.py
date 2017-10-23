from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.authentication.models import Token, PhoneAuthUser
from src.apps.authentication.utils import Gender
from src.apps.clients.models import Client, Address
from src.apps.clients.views import ClientUpdateView, Me
from src.apps.core import utils
from src.apps.core.models import Location


class UpdateClientTestCase(APITestCase):
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

    def test_update_address(self):
        client_id = self.client_object.id
        resp = self.client.patch(reverse(ClientUpdateView.view_name, args=[client_id]), data={
            'address': {
                'apt_number': 790,
                'location': {
                    'lat': 200
                }
            }
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # token hasn't changed
        self.assertIn('token', resp.data)

        self.client_object = Client.objects.get(pk=client_id)
        # apt number changed
        self.assertEqual(self.client_object.address.apt_number, 790)
        # lat changed
        self.assertEqual(self.client_object.address.location.lat, 200)

    def test_update_tip(self):
        client_id = self.client_object.id
        resp = self.client.patch(reverse(ClientUpdateView.view_name, args=[client_id]), data={
            'tip': 3
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # token hasn't changed
        self.assertIn('token', resp.data)

        self.client_object = Client.objects.get(pk=client_id)
        # apt number changed
        self.assertEqual(self.client_object.tip, 3)

    def test_update_phone(self):
        client_id = self.client_object.id
        resp = self.client.patch(reverse(ClientUpdateView.view_name, args=[client_id]), data={
            'phone': '88005553535'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('token', resp.data)
        new_token = resp.data['token']

        self.client_object = Client.objects.get(pk=client_id)
        # phone is updated
        self.assertEqual(self.client_object.user.phone, '88005553535')

        resp = self.client.get(reverse(Me.view_name))
        # old token is disabled
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {new_token}')

        resp = self.client.get(reverse(Me.view_name))
        # new token is ok
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_update_name_fail(self):
        resp = self.client.patch(reverse(ClientUpdateView.view_name, args=[self.client_object.id]), data={
            'first_name': 'A new name'
        }, format='json')
        # changing first_name is forbidden
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
