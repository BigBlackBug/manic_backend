from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.masters.models import Master
from src.apps.masters.test import make_everything, make_token
from src.apps.masters.views import MasterDetailView


class MasterDetailTestCase(APITestCase):
    def setUp(self):
        make_everything()
        self.token = make_token()
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_master_does_not_exist(self):
        resp = self.client.get(reverse(MasterDetailView.view_name, args=[10]))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_master_exists(self):
        master = Master.objects.get(first_name='VASYA')
        resp = self.client.get(
            reverse(MasterDetailView.view_name, args=[master.id]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
