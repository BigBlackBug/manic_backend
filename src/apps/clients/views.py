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
        if request.user.has_account():
            raise PermissionDenied(detail='This phone already has an associated account')
        return super().post(request, **kwargs)


class ClientUpdateView(generics.UpdateAPIView):
    view_name = 'client-update'
    permission_classes = (IsAuthenticated, IsClientIDCorrect)
    serializer_class = ClientSerializer
    queryset = Client.objects.all()


class ClientAvatarUpdateView(APIView):
    view_name = 'client-avatar-update'

    parser_classes = (parsers.MultiPartParser,)
    permission_classes = (IsAuthenticated, IsClientIDCorrect)

    def patch(self, request, **kwargs):
        phone_user = request.user

        serializer = ImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image = serializer.validated_data['image']
        phone_user.client.avatar = image
        phone_user.client.save()

        return Response(status=status.HTTP_201_CREATED, data={
            'image': phone_user.client.avatar.url
        })
