from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from src.apps.masters.models import Master
from src.apps.masters.test import make_token, make_everything
from src.apps.masters.views import MasterScheduleView


class MasterScheduleTestCase(TestCase):
    def setUp(self):
        make_everything()
        self.token = make_token()
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_master_schedule(self):
        master = Master.objects.get(first_name='VASYA')
        service = master.services.all()[0]
        url = reverse(MasterScheduleView.view_name, args=[master.id])
        resp = self.client.get(f"{url}?service={service.id}")
        print(resp.data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # both days
        # TODO more asserts
        self.assertEqual(len(resp.data), 2)
