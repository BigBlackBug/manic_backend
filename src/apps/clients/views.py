from rest_framework import generics, parsers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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
          'tip': 5,
          'address': {
            'location': {
                'lat': 100,
                'lon': 100,
            }, 'city': 'kazan', 'street_name': 'best street ever',
            'building': '4', 'floor': 2,
            'apt_number': 10,
            'entrance': 6, 'has_intercom': True
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


# class ClientUpdateView(generics.UpdateAPIView):
#     view_name = 'client-update'
#     permission_classes = (IsAuthenticated, IsClientIDCorrect)
#     serializer_class = ClientSerializer
#     queryset = Client.objects.all()


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
