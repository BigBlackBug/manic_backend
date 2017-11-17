from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.authentication.models import Token, PhoneAuthUser
from src.apps.core import utils
from src.apps.masters.models import Master
from src.apps.masters.test import make_master, make_client
from src.apps.masters.views import MasterAvatarUpdateView


class AvatarUpdateTestCase(APITestCase):
    def setUp(self):
        self.master_object = make_master('NAME', 10)
        self.user = self.master_object.user
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_upload(self):
        self.master_object.avatar.delete()
        self.assertEqual(self.master_object.avatar, None)
        resp = self.client.patch(reverse(MasterAvatarUpdateView.view_name,
                                         args=[self.master_object.id]),
                                 data={'image': utils.make_in_memory_image(
                                     'avatar')})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        updated_master = Master.objects.get(pk=self.master_object.id)
        self.assertNotEqual(updated_master.avatar, None)

    def test_upload_wrong_master(self):
        resp = self.client.patch(reverse(MasterAvatarUpdateView.view_name,
                                         args=[100]),
                                 data={'image': utils.make_in_memory_image(
                                     'avatar')})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_no_image(self):
        resp = self.client.patch(reverse(MasterAvatarUpdateView.view_name,
                                         args=[self.master_object.id]))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_not_master(self):
        client_object = make_client()

        token, _ = Token.objects.get_or_create(user=client_object.user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        resp = self.client.patch(reverse(MasterAvatarUpdateView.view_name,
                                         args=[self.master_object.id]),
                                 data={'image': utils.make_in_memory_image(
                                     'avatar')})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
