from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.authentication.models import PhoneAuthUser, Token
from src.apps.categories.views import UpsaleRecommendationsView
from src.apps.masters.models import Master, TimeSlot, Time
from src.utils.object_creation import make_everything, make_client


class RecommendationTestCase(APITestCase):
    def setUp(self):
        make_everything()
        self.user = PhoneAuthUser.objects.create(phone='777')
        self.client_object = make_client(self.user)
        token, _ = Token.objects.get_or_create(client=self.client_object)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_recommendation(self):
        master = Master.objects.get(first_name='VASYA')
        schedule = master.get_schedule(timezone.now())
        TimeSlot.objects.create(time=Time.objects.create(hour=12, minute=30),
                                taken=False, schedule=schedule)
        TimeSlot.objects.create(time=Time.objects.create(hour=13, minute=00),
                                taken=False, schedule=schedule)
        services = list(master.services.all())
        order_service = services[0]
        # assume the order is almost created for 11:00 and 11:30
        resp = self.client.post(reverse(UpsaleRecommendationsView.view_name), data={
            'date': timezone.now().strftime('%Y-%m-%d'),
            'time': '11:00',
            'order_items': [{
                'locked': False,
                'master_id': master.id,
                'service_ids': [order_service.id]
            }]
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [{
            'master_id': master.id,
            'service_id': services[1].id
        }])
