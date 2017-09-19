from django.utils import timezone
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from src.apps.authentication import sms_verification
from src.apps.core.views import NamedAPIView
from .models import Registration, PhoneAuthUser, Token
from .serializers import RegistrationSerializer, UpdateRegistrationSerializer


class Logout(NamedAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class CreateRegistrationView(NamedAPIView):
    permission_classes = ()

    def post(self, request: Request):
        """
        Creates a registration

        """
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO generate code
        code = sms_verification.generate_code()
        # overwriting the existing registration
        try:
            registration = Registration.objects.filter(phone=serializer.validated_data['phone'])
        except Registration.DoesNotExist:
            registration = serializer.save(verification_code=code)
        else:
            registration.delete()
            registration = serializer.save(verification_code=code)
        return Response(data={'id': registration.id})


class UpdateRegistrationView(NamedAPIView):
    permission_classes = ()

    def patch(self, request: Request, reg_id: str):
        serializer = UpdateRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = request.data
        try:
            registration = Registration.objects.get(pk=reg_id)
        except Registration.DoesNotExist as ex:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            if registration.verification_code != data['verification_code']:
                raise serializers.ValidationError(
                    {'verification_code': ['Verification code is incorrect']})

            if timezone.now() > registration.expires:
                raise serializers.ValidationError(
                    {'verification_code': ['Verification code has expired']})

            user, created = PhoneAuthUser.objects.get_or_create(phone=registration.phone)
            token, _ = Token.objects.get_or_create(user=user)

            # we don't need the registration anymore
            registration.delete()

            return Response(data={'user_id': user.id, 'token': token.key})

    def delete(self, request: Request, reg_id: str):
        """
        Cancels the registration process, i.e. when a user declines the user agreement

        """
        try:
            registration = Registration.objects.get(pk=reg_id)
        except Registration.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            registration.delete()

        return Response(status=status.HTTP_200_OK)
