from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.core import utils
from src.apps.masters.models import Schedule
from src.apps.masters.test import make_master, make_token
from src.apps.masters.views import MasterDetailUpdateView


class MasterDetailTestCase(APITestCase):
    def setUp(self):
        self.master_object = make_master('123', 3)
        token = make_token(master=self.master_object)
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_master_does_not_exist(self):
        resp = self.client.get(
            reverse(MasterDetailUpdateView.view_name, args=[100500]))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_master_exists(self):
        # old schedule
        Schedule.objects.create(master=self.master_object,
                                date=utils.get_date(-2))
        # new schedule
        Schedule.objects.create(master=self.master_object,
                                date=utils.get_date(2))
        # new schedule
        Schedule.objects.create(master=self.master_object,
                                date=utils.get_date(1))
        # todays schedule
        Schedule.objects.create(master=self.master_object,
                                date=utils.get_date(0))
        resp = self.client.get(
            reverse(MasterDetailUpdateView.view_name,
                    args=[self.master_object.id]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # only new schedules are returned
        self.assertEqual(len(resp.data['schedule']), 3)
        # ASC sorted
        self.assertLess(resp.data['schedule'][0]['date'],
                        resp.data['schedule'][1]['date'])
        self.assertLess(resp.data['schedule'][1]['date'],
                        resp.data['schedule'][2]['date'])
