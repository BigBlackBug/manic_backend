from django.utils import timezone
from rest_framework.test import APITestCase

from src.apps.authentication.models import PhoneAuthUser
from src.apps.core import utils
from .models import Master, Location
from .utils import Gender


class MastersTestCase(APITestCase):
    # def setUp(self):
    #     # Every test needs access to the request factory.
    #     self.factory = APIRequestFactory()
    #     self.user = PhoneAuthUser.objects.create(phone='777')
    #     token, _ = Token.objects.get_or_create(user=self.user)
    #
    #     self.client = APIClient()
    #     self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    def setUp(self):
        self.user = PhoneAuthUser.objects.create(phone='777')

    def tearDown(self):
        self.user.delete()

    # def test_smth(self):
    #     profile = UserProfile.objects.create(user=self.user, gender_or_whatever='gen')
    #     client = Client.objects.create(profile=profile, client_field=10)
    # def test_smth2(self):
    #     client = Master.objects.create(user=self.user, first_name='gen',
    #                                    avatar=utils.make_in_memory_image('supername'),
    #                                    gender=Gender.MALE, date_of_birth=timezone.now(),
    #                                    coords=Location.objects.create(lat=10,lon=11),
    #                                    address=Address.objects.create(city='asd'))
