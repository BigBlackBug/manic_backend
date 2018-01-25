from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from src.apps.texts.models import Text
from src.apps.texts.serializers import TextSerializer


class ListCreateTextView(generics.ListCreateAPIView):
    view_name = 'list-create-text'
    queryset = Text.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = TextSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('name', 'key')

    # YES ALL OF THIS TO AVOID RETURNING A LIST
    def get(self, request, *args, **kwargs):
        resp = self.list(request, *args, **kwargs)
        if not resp.data:
            raise NotFound('Text not found')

        return Response(data=resp.data[0])
