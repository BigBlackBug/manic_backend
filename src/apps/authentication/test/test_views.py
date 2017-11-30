import json
from datetime import timedelta
from unittest import mock

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from src.utils.object_creation import make_client
from ..models import Registration, Token, RegistrationType
from ..views import CreateRegistrationView, UpdateRegistrationView, LogoutView


def make_json_body(body):
    return {'data': json.dumps(body), 'content_type': 'application/json'}


@mock.patch('src.apps.authentication.sms_verification.send_code',
            lambda phone, code: True)
class LoginTest(APITestCase):
    def test_create_registration(self):
        response = self.client.post(reverse(CreateRegistrationView.view_name),
                                    **make_json_body({'phone': '111',
                                                      'type': 'CLIENT', }))
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        registrations = list(Registration.objects.filter(phone='111'))

        # created successfully
        self.assertEqual(1, len(registrations))
        self.assertEqual(response.data['id'], registrations[0].id)

    def test_create_two_registration(self):
        # there is registration for this phone
        Registration.objects.create(phone='111', verification_code='0000',
                                    type=RegistrationType.CLIENT,
                                    expires=timezone.now() + timedelta(
                                        minutes=5)
                                    )
        # creating a new one
        response = self.client.post(reverse(CreateRegistrationView.view_name),
                                    **make_json_body({'phone': '111',
                                                      'type': 'CLIENT', }))

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        registrations = list(Registration.objects.filter(phone='111'))

        self.assertEqual(1, len(registrations))
        self.assertEqual(response.data['id'], registrations[0].id)

    def test_confirm_registration_incorrect_reg_id(self):
        url = reverse(UpdateRegistrationView.view_name, args=[100])
        response = self.client.patch(url,
                                     **make_json_body(
                                         {'verification_code': '0000'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_confirm_registration_incorrect_code(self):
        reg = Registration.objects.create(phone='111', verification_code='0000',
                                          type=RegistrationType.CLIENT,
                                          expires=timezone.now() + timedelta(
                                              minutes=5)
                                          )
        response = self.client.patch(
            reverse(UpdateRegistrationView.view_name, args=[reg.id]),
            **make_json_body({'verification_code': '0001'}))
        # wrong code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_registration_long_code(self):
        reg = Registration.objects.create(phone='111', verification_code='0000',
                                          expires=timezone.now() + timedelta(
                                              minutes=5)
                                          )
        response = self.client.patch(
            reverse(UpdateRegistrationView.view_name, args=[reg.id]),
            **make_json_body({'verification_code': '00000'}))
        # long code
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_registration_expired(self):
        reg = Registration.objects.create(phone='111', verification_code='0000',
                                          type=RegistrationType.CLIENT,
                                          expires=timezone.now() - timedelta(
                                              minutes=5))
        response = self.client.patch(
            reverse(UpdateRegistrationView.view_name, args=[reg.id]),
            **make_json_body({'verification_code': '0000'}))
        # reg expired
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_registration_ok(self):
        reg = Registration.objects.create(phone='111', verification_code='0000',
                                          type=RegistrationType.CLIENT,
                                          expires=timezone.now() + timedelta(
                                              minutes=5)
                                          )

        response = self.client.patch(
            reverse(UpdateRegistrationView.view_name, args=[reg.id]),
            **make_json_body({'verification_code': '0000'}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

        with self.assertRaises(Registration.DoesNotExist):
            Registration.objects.get(phone='111')

    def test_logout_ok(self):
        token, _ = Token.objects.get_or_create(client=make_client())

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        # first time ok
        response = self.client.post(reverse(LogoutView.view_name))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # second time gives unauthorized
        response = self.client.post(reverse(LogoutView.view_name))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_unauthorized(self):
        response = self.client.post(reverse(LogoutView.view_name))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
