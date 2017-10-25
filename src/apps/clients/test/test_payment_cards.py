from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from src.apps.authentication.models import Token, PhoneAuthUser
from src.apps.authentication.utils import Gender
from src.apps.clients.models import Client, Address, PaymentCard
from src.apps.clients.views import AddPaymentCardView, DeletePaymentCardView
from src.apps.core import utils
from src.apps.core.models import Location


class PaymentCardsTestCase(APITestCase):
    def setUp(self):
        self.user = PhoneAuthUser.objects.create(phone='777')
        self.client_object = Client.objects.create(
            user=self.user,
            first_name='client',
            avatar=utils.make_in_memory_image('supername'),
            gender=Gender.MALE,
            date_of_birth=timezone.now(),
            address=Address.objects.create(
                location=Location.objects.create(lat=10, lon=10),
                city='kazan',
                street_name='latstr',
                building='4', floor=2,
                apt_number=79,
                entrance=6,
                has_intercom=True
            )
        )
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_add_card(self):
        client_id = self.client_object.id
        # 'cryptogram', 'client_name_on_card', 'card_number'
        resp = self.client.post(
            reverse(AddPaymentCardView.view_name, args=[client_id]), data={
                'cryptogram': 'AZAZA',
                'client_name_on_card': 'AZAZAZA',
                'card_number': '3333333333333333'
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        self.client_object = Client.objects.get(pk=client_id)
        self.assertEqual(len(self.client_object.payment_cards.all()), 1)
        card = self.client_object.payment_cards.first()
        self.assertEqual(card.cryptogram, 'AZAZA')
        self.assertEqual(card.client_name_on_card, 'AZAZAZA')
        self.assertEqual(card.card_number, '3333333333333333')

    def test_add_card_wrong_card_number_length(self):
        client_id = self.client_object.id
        # 'cryptogram', 'client_name_on_card', 'card_number'
        resp = self.client.post(
            reverse(AddPaymentCardView.view_name, args=[client_id]), data={
                'cryptogram': 'AZAZA',
                'client_name_on_card': 'AZAZAZA',
                'card_number': '3333333333333'
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_card_incorrect_card_number(self):
        client_id = self.client_object.id
        # 'cryptogram', 'client_name_on_card', 'card_number'
        resp = self.client.post(
            reverse(AddPaymentCardView.view_name, args=[client_id]), data={
                'cryptogram': 'AZAZA',
                'client_name_on_card': 'AZAZAZA',
                'card_number': '33qq333333333ff3'
            }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_card(self):
        client_id = self.client_object.id
        card = PaymentCard.objects.create(client=self.client_object, **{
            'cryptogram': 'AZAZA',
            'client_name_on_card': 'AZAZAZA',
            'card_number': '3333333333333333'
        })
        resp = self.client.delete(reverse(DeletePaymentCardView.view_name,
                                          args=[client_id, card.id]),
                                  format='json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        self.client_object = Client.objects.get(pk=client_id)
        self.assertEqual(len(self.client_object.payment_cards.all()), 0)

    def test_delete_card_incorrect_card_id(self):
        client_id = self.client_object.id
        resp = self.client.delete(reverse(DeletePaymentCardView.view_name,
                                          args=[client_id, 100]), format='json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
