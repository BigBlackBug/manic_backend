import logging

from rest_framework import generics, parsers, status, mixins
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.apps.authentication.models import Token
from src.apps.core.permissions import IsClient
from src.apps.core.serializers import ImageSerializer
from .models import Client, PaymentCard
from .permissions import IsClientIDCorrect
from .serializers import ClientSerializer, PaymentCardSerializer

logger = logging.getLogger(__name__)


class ClientCreateView(generics.CreateAPIView):
    view_name = 'client-list'
    queryset = Client.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ClientSerializer

    def post(self, request, **kwargs):
        """
        Creates a client

        Input:
        ```
        {
          'first_name': 'Maria',
          'gender': 'F/M',
          'date_of_birth': '1988-10-29',
          'tip': 5, //**optional**
          'address': { //**optional**
            'location': {
                'lat': 100,
                'lon': 100,
            },
            'city': 'kazan',
            'street_name': 'best street ever',
            'building': '4', 'floor': 2,
            'apt_number': 10,
            'entrance': 6,
            'has_intercom': True
          }
        }
        ```

        Response:
        201 Created

        403 Forbidden - If an account is already associated with this phone

        400 Bad Request
        """
        if request.user.has_account():
            raise PermissionDenied(
                detail='This phone already has an associated account')
        return super().post(request, **kwargs)


class ClientUpdateView(mixins.UpdateModelMixin, GenericAPIView):
    view_name = 'client-update'
    permission_classes = (IsAuthenticated, IsClientIDCorrect)
    serializer_class = ClientSerializer
    queryset = Client.objects.all()

    def patch(self, request, *args, **kwargs):
        """
        Updates client info.

        Allowed fields: **phone, tip, address**.
        Address json may contain any number of fields.

        Input:
        ```
        {
          'phone': '88005553535',
          'tip': 5,
          'address': {
            'location': {
                'lon': 100,
            },
            'city': 'kazan',
            'street_name': 'best street ever',
            'has_intercom': True
          }
        }
        ```

        Response:
        200 OK ```{'token': 'new-auth-token'}```
        If the user updates his phone number, his old auth token is invalidated
        for the sake of security.

        400 Bad Request
        """
        super().partial_update(request, *args, **kwargs)
        # old token should not be valid
        request.user.auth_token.delete()

        token, _ = Token.objects.get_or_create(user=request.user)
        return Response(data={
            'token': token.key
        })


class ClientAvatarUpdateView(APIView):
    view_name = 'client-avatar-update'

    parser_classes = (parsers.MultiPartParser,)
    permission_classes = (IsAuthenticated, IsClientIDCorrect)

    def patch(self, request, **kwargs):
        """
        Adds or replaces the avatar of the client

        Input:

        multi-part form data where `image` field contains the image

        Response:
        201 Created `{'image':'url-to-the-image'}`

        400 Bad Request
        """
        phone_user = request.user

        logger.info(f'Updating an avatar for'
                    f'client {phone_user.client.first_name}, '
                    f'id={phone_user.client.id}')

        serializer = ImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image = serializer.validated_data['image']
        phone_user.client.avatar = image
        phone_user.client.save()

        return Response(status=status.HTTP_201_CREATED, data={
            'image': phone_user.client.avatar.url
        })


class Me(generics.RetrieveAPIView):
    view_name = 'me'
    permission_classes = (IsAuthenticated, IsClient)
    serializer_class = ClientSerializer

    def get_object(self):
        return self.request.user.client

    def get(self, request, *args, **kwargs):
        """
        Returns a representation of current logged-in client.

        Response:
        200 OK
                ```
        {
          'first_name': 'Maria',
          'phone': '88005553535'
          'gender': 'F/M',
          'date_of_birth': '1988-10-29',
          'tip': 5, //**optional**
          'address': { //**optional**
            'location': {
                'lat': 100,
                'lon': 100,
            },
            'city': 'kazan',
            'street_name': 'best street ever',
            'building': '4', 'floor': 2,
            'apt_number': 10,
            'entrance': 6,
            'has_intercom': True
          },
          'payment_cards': [{
            'id':1,
            'cryprogram':'cryptogram',
            'client_name_on_card':'VASYA VASIN',
            'card_number':'0000000000000000'
          }]
        }
        ```
        """
        return super().get(request, *args, **kwargs)


class AddPaymentCardView(generics.CreateAPIView):
    view_name = 'add-payment-card'
    permission_classes = (IsAuthenticated, IsClientIDCorrect)
    queryset = Client.objects.all()
    serializer_class = PaymentCardSerializer

    def post(self, request, *args, **kwargs):
        """
        Adds a payment card to the current client

        Input:
        ```
        {
          //generated by cloudpayment
          'cryptogram': 'AZAZA',
          'client_name_on_card': 'AZAZAZA',
          'card_number': '3333333333333333'
        }
        ```

        Response:

        201 Created

        400 Bad Request
        """
        return super().post(request, *args, **kwargs)


class DeletePaymentCardView(generics.DestroyAPIView):
    view_name = 'add-payment-card'
    permission_classes = (IsAuthenticated, IsClientIDCorrect)
    queryset = Client.objects.all()
    serializer_class = PaymentCardSerializer

    def get_object(self):
        card_id = self.kwargs['card_id']
        client = self.request.user.client
        try:
            return client.payment_cards.get(pk=card_id)
        except PaymentCard.DoesNotExist:
            raise NotFound(f'Payment card with id {card_id} is not found')

    def delete(self, request, *args, **kwargs):
        """
        Removes a payment card from a client

        Response:
        204 No Content

        400 Bad Request
        """
        return super().delete(request, *args, **kwargs)
