from datetime import datetime

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.authentication.models import Token, PhoneAuthUser
from src.apps.clients.models import Client
from src.apps.clients.views import ClientUpdateView
from src.utils.object_creation import make_client


class UpdateClientTestCase(APITestCase):
    def setUp(self):
        self.user = PhoneAuthUser.objects.create(phone='777')
        self.client_object = make_client(self.user)
        token, _ = Token.objects.get_or_create(client=self.client_object)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_update_name(self):
        client_id = self.client_object.id
        resp = self.client.patch(
            reverse(ClientUpdateView.view_name, args=[client_id]), data={
                'first_name': 'Anna'
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.client_object = Client.objects.get(pk=client_id)
        # name changed
        self.assertEqual(self.client_object.first_name, 'Anna')

    def test_update_phone_fail(self):
        resp = self.client.patch(
            reverse(ClientUpdateView.view_name, args=[self.client_object.id]),
            data={
                'phone': '88005553536'
            }, format='json')
        # changing phone is forbidden
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_tip(self):
        client_id = self.client_object.id
        resp = self.client.patch(
            reverse(ClientUpdateView.view_name, args=[client_id]), data={
                'tip': 3
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.client_object = Client.objects.get(pk=client_id)
        # apt number changed
        self.assertEqual(self.client_object.tip, 3)

    def test_update_dob(self):
        client_id = self.client_object.id
        resp = self.client.patch(
            reverse(ClientUpdateView.view_name, args=[client_id]), data={
                'date_of_birth': '1999-10-20'
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.client_object = Client.objects.get(pk=client_id)
        # apt number changed
        self.assertEqual(self.client_object.date_of_birth,
                         datetime.strptime('1999-10-20', '%Y-%m-%d').date())
