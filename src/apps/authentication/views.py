import logging

from django.conf import settings
from django.utils import timezone
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from src.apps.authentication import sms_verification
from src.apps.core.views import NamedAPIView
from .models import Registration, PhoneAuthUser, Token
from .serializers import RegistrationSerializer, UpdateRegistrationSerializer

logger = logging.getLogger(__name__)


class LogoutView(NamedAPIView):
    """
    Logs a client out

    Response:
    200 OK

    401 Unauthorized
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request):
        request.user.auth_token.delete()
        logger.info(f'User {request.user.phone} has logged out')
        return Response(status=status.HTTP_200_OK)


class CreateRegistrationView(NamedAPIView):
    permission_classes = ()

    def post(self, request: Request):
        """
        Creates or replaces a registration for the provided number

        Input:
        ```{ 'phone':'88005553535' }```

        Response:
        201 Created
        ``` { 'id':100500 } ```
        500 Internal Server Error

        If there was an issue sending an sms
        """
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data['phone']
        if not settings.DEBUG:
            code = sms_verification.generate_code(phone)
            logger.info(f'Generated code {code} for the phone {phone}')
            # will raise exception
            sms_verification.send_code(phone, code)
            logger.info(f'SMS with auth code to phone {phone} '
                        f'has been sent successfully')
        else:
            code = '0000'

        # overwriting the existing registration
        try:
            registration = Registration.objects.filter(phone=phone)
        except Registration.DoesNotExist:
            logger.debug(f'Creating a new registration for phone {phone}')
            registration = serializer.save(verification_code=code)
        else:
            logger.debug(f'Overwriting previous registration for phone {phone}')
            registration.delete()
            registration = serializer.save(verification_code=code)

        logger.info(f'Created a registration for phone {phone}')
        return Response(data={'id': registration.id},
                        status=status.HTTP_201_CREATED)


class UpdateRegistrationView(NamedAPIView):
    permission_classes = ()

    def patch(self, request: Request, reg_id: str):
        """
        Confirms a registration

        Provides an authentication token for the client that
        is to be used in all subsequent requests to the API

        Input:
        ```{ 'verification_code':'0000' }```

        Response:
        200 OK
        ``` { 'user_id':100500, 'token':'TOKEN' } ```

        404 Not Found

        400 Bad Request
        """
        serializer = UpdateRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = request.data
        try:
            registration = Registration.objects.get(pk=reg_id)
        except Registration.DoesNotExist as ex:
            logger.debug(f'Registration with id {reg_id} was not found')
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            if registration.verification_code != data['verification_code']:
                raise serializers.ValidationError(
                    {'verification_code': ['Verification code is incorrect']})

            if timezone.now() > registration.expires:
                raise serializers.ValidationError(
                    {'verification_code': ['Verification code has expired']})

            logger.debug(f'Creating a new token for phone {registration.phone}')
            user, created = PhoneAuthUser.objects.get_or_create(
                phone=registration.phone)
            token, _ = Token.objects.get_or_create(user=user)

            logger.debug(f'Deleting the registration {registration.phone}')
            # we don't need the registration anymore
            registration.delete()

            return Response(data={'user_id': user.id, 'token': token.key})

    def delete(self, request: Request, reg_id: str):
        """
        Cancels the registration process,
        i.e. when a user declines the user agreement

        Input:

        Response:
        200 OK

        404 Not Found

        400 Bad Request
        """
        try:
            registration = Registration.objects.get(pk=reg_id)
        except Registration.DoesNotExist:
            logger.debug(f'Registration with id {reg_id} was not found')
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            logger.debug(f'Deleting the registration {registration.phone}')
            registration.delete()

        return Response(status=status.HTTP_200_OK)
