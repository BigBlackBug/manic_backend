from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.authentication.models import Token
from src.apps.core import utils
from src.apps.masters.models import Master, PortfolioImageStatus, PortfolioImage
from src.apps.masters.test import make_master, make_client
from src.apps.masters.views import AddPortfolioItemsView, \
    AddPortfolioItemDescriptionView


class UploadTestCase(APITestCase):
    def setUp(self):
        self.master_object = make_master('VASYA', 10)
        token, _ = Token.objects.get_or_create(master=self.master_object)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_upload_multiple(self):
        self.assertEqual(len(self.master_object.portfolio.all()), 0)
        resp = self.client.post(reverse(AddPortfolioItemsView.view_name,
                                        args=[self.master_object.id]),
                                data={'images': [
                                    utils.make_in_memory_image(
                                        'avatar'),
                                    utils.make_in_memory_image(
                                        'avatar2')]
                                },
                                format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(resp.data), 2)
        updated_master = Master.objects.get(pk=self.master_object.id)
        self.assertIsNotNone(updated_master.portfolio)
        self.assertEqual(len(updated_master.portfolio.all()), 2)
        self.assertEqual(updated_master.portfolio.first().status,
                         PortfolioImageStatus.ON_MODERATION)

    def test_upload_one(self):
        self.assertEqual(len(self.master_object.portfolio.all()), 0)
        resp = self.client.post(reverse(AddPortfolioItemsView.view_name,
                                        args=[self.master_object.id]),
                                data={
                                    'images': [utils.make_in_memory_image(
                                        'avatar')],
                                }, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(resp.data), 1)
        updated_master = Master.objects.get(pk=self.master_object.id)
        self.assertIsNotNone(updated_master.portfolio)
        self.assertEqual(len(updated_master.portfolio.all()), 1)
        self.assertEqual(updated_master.portfolio.first().status,
                         PortfolioImageStatus.ON_MODERATION)
        self.assertEqual(updated_master.portfolio.first().description, '')

    def test_upload_wrong_master(self):
        resp = self.client.post(reverse(AddPortfolioItemsView.view_name,
                                        args=[100]),
                                data={'image': [utils.make_in_memory_image(
                                    'avatar')]}, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_no_image(self):
        resp = self.client.post(reverse(AddPortfolioItemsView.view_name,
                                        args=[self.master_object.id]))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_not_master(self):
        client = make_client()

        token, _ = Token.objects.get_or_create(client=client)

        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        resp = self.client.post(reverse(AddPortfolioItemsView.view_name,
                                        args=[self.master_object.id]),
                                data={'images': [utils.make_in_memory_image(
                                    'avatar')]}, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class AddDescriptionTestCase(APITestCase):
    def setUp(self):
        self.master_object = make_master('VASYA', 10)
        token, _ = Token.objects.get_or_create(master=self.master_object)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_set_description(self):
        self.assertEqual(len(self.master_object.portfolio.all()), 0)
        image = PortfolioImage.objects.create(master=self.master_object,
                                              image=utils.make_in_memory_image(
                                                  'kek'))

        resp = self.client.patch(
            reverse(AddPortfolioItemDescriptionView.view_name,
                    args=[self.master_object.id]),
            data=[{'image_id': image.id,
                   'description': 'superdescription'}],
            format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        image = PortfolioImage.objects.get(pk=image.id)
        self.assertEqual(image.description, 'superdescription')
