import datetime
from unittest import mock

from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from src.apps.authentication.models import PhoneAuthUser, Token
from src.apps.masters import gmaps_utils
from src.apps.masters.models import Master
from src.apps.masters.test import make_everything, make_client, make_order
from src.apps.masters.views import MasterScheduleView


class MasterScheduleTestCase(TestCase):
    def setUp(self):
        make_everything()
        self.user = PhoneAuthUser.objects.create(phone='777')
        self.client_object = make_client(self.user)
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    @mock.patch.object(gmaps_utils, '_calculate_eta')
    def test_master_schedule(self, _calculate_eta):
        master = Master.objects.get(first_name='VASYA')
        service = master.services.all()[0]
        # manually creating an order
        make_order(client=make_client(), master=master, service=service,
                   time=datetime.time(hour=10, minute=30))

        # assume all slots are reachable
        _calculate_eta.return_value = 10

        url = reverse(MasterScheduleView.view_name, args=[master.id])
        resp = self.client.get(f"{url}?service={service.id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # both days
        self.assertEqual(len(resp.data), 2)
        # two slots
        day_one_slots = resp.data[0]['time_slots']
        self.assertEqual(len(day_one_slots), 2)
        # two slots
        day_two_slots = resp.data[1]['time_slots']
        self.assertEqual(len(day_two_slots), 2)
