import random

from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.authentication.models import Token, PhoneAuthUser
from src.apps.authentication.utils import Gender
from src.apps.clients.models import Client, Address
from src.apps.clients.views import ClientAvatarUpdateView
from src.apps.core import utils
from src.apps.core.models import Location
from src.apps.masters.models import Master


class UploadTestCase(APITestCase):
    def setUp(self):
        self.user = PhoneAuthUser.objects.create(phone=random.randint(1000,10000))
        self.client_object = Client.objects.create(user=self.user, first_name='client',
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

    def test_upload(self):
        self.assertEqual(self.client_object.avatar, None)
        resp = self.client.patch(reverse(ClientAvatarUpdateView.view_name,
                                         args=[self.client_object.id]),
                                 data={'image': utils.make_in_memory_image('avatar')})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        updated_client = Client.objects.get(pk=self.client_object.id)
        self.assertNotEqual(updated_client.avatar, None)

    def test_upload_wrong_client(self):
        resp = self.client.patch(reverse(ClientAvatarUpdateView.view_name,
                                         args=[100]),
                                 data={'image': utils.make_in_memory_image('avatar')})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_no_image(self):
        resp = self.client.patch(reverse(ClientAvatarUpdateView.view_name,
                                         args=[self.client_object.id]))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_not_client(self):
        master_user = PhoneAuthUser.objects.create(phone='666')
        master = Master.objects.create(user=master_user, first_name='master',
                                       avatar=utils.make_in_memory_image('supername'),
                                       gender=Gender.MALE, date_of_birth=timezone.now(),
                                       location=Location.objects.create(lat=10, lon=2))

        token, _ = Token.objects.get_or_create(user=master_user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        resp = self.client.patch(reverse(ClientAvatarUpdateView.view_name,
                                         args=[self.client_object.id]),
                                 data={'image': utils.make_in_memory_image('avatar')})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
