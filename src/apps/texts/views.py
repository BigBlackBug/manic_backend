from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

from src.apps.texts.models import Text
from src.apps.texts.serializers import TextSerializer


class ListCreateTextView(generics.ListCreateAPIView):
    view_name = 'list-create-text'
    queryset = Text.objects.all()
    permission_classes = ()
    serializer_class = TextSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('name', 'key')

    def get(self, request, *args, **kwargs):
        """
        Searches for a text, or returns a list of all texts

        Query params: `key`, `name`

        Response:

        200 OK
        ```
        [{
          'key':'kekeke',
          'name':'A very large KEK',
          'text':'This kek is soo big, it's unbelievable'
        }]

        ```
        """
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Creates a text

        Input:
        ```
        {
          //UNIQUE
          'key':'kekeke',
          //UNIQUE
          'name':'A very large KEK',
          'text':'This kek is soo big, it's unbelievable'
        }

        ```

        Response:

        200 OK
        {
          'key':'kekeke',
          'name':'A very large KEK',
          'text':'This kek is soo big, it's unbelievable'
        }

        400 Bad Request
        """
        return self.create(request, *args, **kwargs)
