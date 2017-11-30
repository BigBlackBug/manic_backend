import datetime
from unittest import mock

from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from src.apps.authentication.models import PhoneAuthUser, Token
from src.apps.masters import gmaps_utils
from src.apps.masters.models import Master
from src.utils.object_creation import make_everything, make_client, make_order
from src.apps.masters.views import MasterSearchView


class MasterSearchViewTestCase(TestCase):
    def setUp(self):
        make_everything()
        self.user = PhoneAuthUser.objects.create(phone='777')
        self.client_object = make_client(self.user)
        token, _ = Token.objects.get_or_create(client=self.client_object)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    @mock.patch.object(gmaps_utils, '_calculate_eta')
    def test_master_search_only_service(self, _calculate_eta):
        master = Master.objects.get(first_name='VASYA')
        service = master.services.all()[0]
        # manually creating an order
        make_order(client=make_client(), master=master, service=service,
                   order_time=datetime.time(hour=10, minute=30))

        # assume all slots are reachable
        _calculate_eta.return_value = 10

        url = reverse(MasterSearchView.view_name)
        resp = self.client.get(f"{url}?service={service.id}&coordinates=10,20")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # no favorites in this test
        favorites = resp.data['favorites']
        self.assertEqual(len(favorites), 0)
        others = resp.data['others']
        # both do at least one service in the following week
        self.assertEqual(len(others), 1)

        # two days with slots
        day_one_slots = others[0]['available_slots']
        self.assertEqual(len(day_one_slots), 2)
        # TODO MORE TESTS
