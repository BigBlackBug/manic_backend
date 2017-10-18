from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from src.apps.core.permissions import IsClient
from .models import Order
from .serializers import OrderSerializer


class OrderCreateView(generics.CreateAPIView):
    view_name = 'order-create'
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated, IsClient)
    serializer_class = OrderSerializer

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
        super().post(request, *args, **kwargs)
