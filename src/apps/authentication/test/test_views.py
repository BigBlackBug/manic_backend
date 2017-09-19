import json
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from src.apps.authentication.models import Registration
from src.apps.authentication.views import CreateRegistrationView, UpdateRegistrationView


def make_json_body(body):
    return {'data': json.dumps(body), 'content_type': 'application/json'}


class LoginTest(TestCase):
    # def setUp(self):
    #     # Every test needs access to the request factory.
    #     self.factory = APIRequestFactory()
    #     self.user = PhoneAuthUser.objects.create(phone='777')
    #     token, _ = Token.objects.get_or_create(user=self.user)
    #
    #     self.client = APIClient()
    #     self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_create_registration(self):
        response = self.client.post(reverse(CreateRegistrationView.view_name),
                                    **make_json_body({'phone': '111'}))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        registrations = list(Registration.objects.filter(phone='111'))

        # created succesfully
        self.assertEqual(1, len(registrations))
        self.assertEqual(response.data['id'], registrations[0].id)

    def test_create_two_registration(self):
        # there is registration for this phone
        Registration.objects.create(phone='111', verification_code='0000')
        # creating a new one
        response = self.client.post(reverse(CreateRegistrationView.view_name),
                                    **make_json_body({'phone': '111'}))

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        registrations = list(Registration.objects.filter(phone='111'))

        self.assertEqual(1, len(registrations))
        self.assertEqual(response.data['id'], registrations[0].id)

    def test_confirm_registration_incorrect_reg_id(self):
        url = reverse(UpdateRegistrationView.view_name, args=[100])
        response = self.client.patch(url,
                                     **make_json_body({'verification_code': '0000'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_confirm_registration_incorrect_code(self):
        reg = Registration.objects.create(phone='111', verification_code='0000')
        response = self.client.patch(reverse(UpdateRegistrationView.view_name, args=[reg.id]),
                                     **make_json_body({'verification_code': '0001'}))
        # wrong code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_registration_long_code(self):
        reg = Registration.objects.create(phone='111', verification_code='0000')
        response = self.client.patch(reverse(UpdateRegistrationView.view_name, args=[reg.id]),
                                     **make_json_body({'verification_code': '00000'}))
        # long code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_registration_expired(self):
        reg = Registration.objects.create(phone='111', verification_code='0000',
                                          expires=timezone.now() - timedelta(minutes=5))
        response = self.client.patch(reverse(UpdateRegistrationView.view_name, args=[reg.id]),
                                     **make_json_body({'verification_code': '0000'}))
        # reg expired
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_registration_ok(self):
        reg = Registration.objects.create(phone='111', verification_code='0000')

        response = self.client.patch(reverse(UpdateRegistrationView.view_name, args=[reg.id]),
                                     **make_json_body({'verification_code': '0000'}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user_id', response.data)
        self.assertIn('token', response.data)

        with self.assertRaises(Registration.DoesNotExist):
            Registration.objects.get(phone='111')
