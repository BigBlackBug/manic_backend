from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.authentication.models import Token, PhoneAuthUser
from src.apps.authentication.utils import Gender
from src.apps.categories.models import Service
from src.apps.core import utils
from src.apps.masters.models import Master, MasterStatus
from src.apps.masters.test import make_category, make_client
from src.apps.masters.views import MasterListCreateView


class CreateMasterTestCase(APITestCase):
    def setUp(self):
        make_category('Сервис')
        self.user = PhoneAuthUser.objects.create(phone='777')
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_create_client_existing_account(self):
        old_user = make_client().user
        token, _ = Token.objects.get_or_create(user=old_user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        resp = self.client.post(reverse(MasterListCreateView.view_name), data={
            'first_name': 'SUPER_MASTER',
            'gender': Gender.MALE,
            'date_of_birth': utils.get_date(-100),
            'email': 'a@a.com',
            # 'about':'about',
            'services': [service.id for service in Service.objects.all()]
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_master(self):
        resp = self.client.post(reverse(MasterListCreateView.view_name), data={
            'first_name': 'SUPER_MASTER',
            'gender': Gender.MALE,
            'date_of_birth': utils.get_date(-100),
            'email': 'a@a.com',
            # 'about':'about',
            'services': [service.id for service in Service.objects.all()]
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_master = Master.objects.get(first_name='SUPER_MASTER')
        self.assertEqual(new_master.status, MasterStatus.ON_REVIEW)
        self.assertEqual(new_master.gender, Gender.MALE)
        self.assertEqual(new_master.email, 'a@a.com')
        self.assertEqual(len(new_master.services.all()),
                         len(Service.objects.all()))