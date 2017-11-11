from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.authentication.models import Token
from src.apps.core import utils
from src.apps.masters.models import Master, PortfolioOrderStatus
from src.apps.masters.test import make_master, make_client
from src.apps.masters.views import AddPortfolioItemsView


class UploadTestCase(APITestCase):
    def setUp(self):
        self.master_object = make_master('VASYA', 10)
        self.user = self.master_object.user
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_upload(self):
        self.assertEqual(len(self.master_object.portfolio.all()), 0)
        resp = self.client.patch(reverse(AddPortfolioItemsView.view_name,
                                         args=[self.master_object.id]),
                                 data={
                                     'image': utils.make_in_memory_image(
                                         'avatar'),
                                     'description': '1'
                                 })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        updated_master = Master.objects.get(pk=self.master_object.id)
        self.assertIsNotNone(updated_master.portfolio)
        self.assertEqual(len(updated_master.portfolio.all()), 1)
        self.assertEqual(updated_master.portfolio.first().status,
                         PortfolioOrderStatus.ON_MODERATION)

    def test_upload_no_description(self):
        self.assertEqual(len(self.master_object.portfolio.all()), 0)
        resp = self.client.patch(reverse(AddPortfolioItemsView.view_name,
                                         args=[self.master_object.id]),
                                 data={
                                     'image': utils.make_in_memory_image(
                                         'avatar'),
                                 })
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        updated_master = Master.objects.get(pk=self.master_object.id)
        self.assertIsNotNone(updated_master.portfolio)
        self.assertEqual(len(updated_master.portfolio.all()), 1)
        self.assertEqual(updated_master.portfolio.first().status,
                         PortfolioOrderStatus.ON_MODERATION)
        self.assertEqual(updated_master.portfolio.first().description, '')

    def test_upload_wrong_master(self):
        resp = self.client.patch(reverse(AddPortfolioItemsView.view_name,
                                         args=[100]),
                                 data={'image': utils.make_in_memory_image(
                                     'avatar')})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_no_image(self):
        resp = self.client.patch(reverse(AddPortfolioItemsView.view_name,
                                         args=[self.master_object.id]))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_not_master(self):
        client = make_client()

        token, _ = Token.objects.get_or_create(user=client.user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        resp = self.client.patch(reverse(AddPortfolioItemsView.view_name,
                                         args=[self.master_object.id]),
                                 data={'image': utils.make_in_memory_image(
                                     'avatar'), 'description': '12'})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
