from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter

from src.apps.clients.models import Client
from src.apps.core.permissions import IsAdmin
from ..serializers import ClientSerializer


class ClientListView(generics.ListAPIView):
    view_name = 'client-list'
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('^first_name',)
    ordering = ('first_name',)

    def get(self, request, *args, **kwargs):
        """
        Returns a list of clients

        Response:
        200 OK
        ```
        {
          'id': 1,
          'first_name': 'Maria',
          'status': 'VERIFIED',
          'avatar':'link-to-image',
          'phone': '88005553535'
          'gender': 'F/M',
          'date_of_birth': '1988-10-29',
          'tip': 5,
          'addresses': [{
            'location': {
                'lat': 100,
                'lon': 100,
            },
            'city': 'kazan',
            'street_name': 'best street ever',
            'building': '4', 'floor': 2,
            'apt_number': 10,
            'entrance': 6,
            'has_intercom': True,
            'home_address': True/False,
            'comment': 'please call before knocking'
          }],
          'payment_cards': [{
            'id':1,
            'cryptogram':'cryptogram',
            'client_name_on_card':'VASYA VASIN',
            'card_number':'0000000000000000'
          }]
        }
        ```
        """
        return super().get(request, *args, **kwargs)
