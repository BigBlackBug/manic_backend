from rest_framework import generics, parsers, status
from rest_framework.exceptions import PermissionDenied, MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.apps.authentication.models import Token
from src.apps.core.permissions import IsClient
from src.apps.core.serializers import ImageSerializer
from .models import Client
from .permissions import IsClientIDCorrect
from .serializers import ClientSerializer


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
            raise PermissionDenied(detail='This phone already has an associated account')
        return super().post(request, **kwargs)


class ClientUpdateView(generics.UpdateAPIView):
    view_name = 'client-update'
    permission_classes = (IsAuthenticated, IsClientIDCorrect)
    serializer_class = ClientSerializer
    queryset = Client.objects.all()

    def put(self, request, *args, **kwargs):
        raise MethodNotAllowed('put')

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
        If the user updates his phone number, his old auth token is invalidated for the sake
        of security.

        400 Bad Request
        """
        super().patch(request, *args, **kwargs)
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
          }
        }
        ```
        """
        return super().get(request, *args, **kwargs)
