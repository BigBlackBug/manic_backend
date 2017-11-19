import random

from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.authentication.models import Token, PhoneAuthUser
from src.apps.authentication.utils import Gender
from src.apps.clients.models import Client, Address
from src.apps.clients.views import ClientAvatarUpdateView, MeClient
from src.apps.core import utils
from src.apps.core.models import Location
from src.apps.masters.models import Master
from src.apps.masters.test import make_client, make_master


class UploadTestCase(APITestCase):
    def setUp(self):
        self.user = PhoneAuthUser.objects.create(
            phone=random.randint(1000, 10000))
        self.client_object = make_client(self.user)
        token, _ = Token.objects.get_or_create(client=self.client_object)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_upload(self):
        self.client_object.avatar.delete()
        self.assertEqual(self.client_object.avatar, None)
        resp = self.client.patch(reverse(ClientAvatarUpdateView.view_name,
                                         args=[self.client_object.id]),
                                 data={'image': utils.make_in_memory_image(
                                     'avatar')})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        updated_client = Client.objects.get(pk=self.client_object.id)
        self.assertNotEqual(updated_client.avatar, None)

    def test_upload_wrong_client(self):
        resp = self.client.patch(reverse(ClientAvatarUpdateView.view_name,
                                         args=[100]),
                                 data={'image': utils.make_in_memory_image(
                                     'avatar')})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_no_image(self):
        resp = self.client.patch(reverse(ClientAvatarUpdateView.view_name,
                                         args=[self.client_object.id]))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_not_client(self):
        master_user = make_master('123',22)
        token, _ = Token.objects.get_or_create(master=master_user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        resp = self.client.patch(reverse(ClientAvatarUpdateView.view_name,
                                         args=[self.client_object.id]),
                                 data={'image': utils.make_in_memory_image(
                                     'avatar')})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
