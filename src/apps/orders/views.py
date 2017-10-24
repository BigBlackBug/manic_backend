from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from src.apps.core.permissions import IsClient
from .models import Order
from .serializers import OrderCreateSerializer, OrderListSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    view_name = 'order-list-create'
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated, IsClient)

    def post(self, request: Request, *args, **kwargs):
        """
        Creates an order

        Input:

        An example input for a composite order
        ```
        {
          'date': '2017-10-18',
          'time': '11:00',
          'order_items': [{
            'master_id': 10,
            'service_ids': [25]
          }, {
             'master_id': 11,
             'service_ids': [16]
          }],
          'special': {
            'type': 'composite'
          }
        }
        ```

        An example input for a simple order (one master doing
        two services in a row)

        ```
        {
          'date': '2017-10-18',
          'time': '11:00',
          'order_items': [{
            'master_id': 10,
            'service_ids': [25, 26]
          }]
        }
        ```

        Response:

        201 Created

        400 Bad Request
        """
        return super().post(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        return queryset.filter(client=self.request.user.client).order_by('-date')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderListSerializer

    def get(self, request, *args, **kwargs):
        """
        Returns a list of orders of the current client, ordered by date

        Response:

        200 OK
        ```
        [{
          'date': '2017-10-18',
          'time': '11:00',
          'special': {},
          'order_items': [{
            'service': {
              'name': 'super service',
              'cost': 100,
              'category':{
                'name': 'super category'
              }
            },
            'master': {
                'first_name': 'Vasya',
                'avatar': 'url-to-avatar'
            }]
        }]
        ```

        """
        return super().get(request, *args, **kwargs)


class CancelOrderView(generics.DestroyAPIView):
    view_name = 'cancel-order'
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated, IsClient)
