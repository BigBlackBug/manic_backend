from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from src.apps.core.permissions import IsClient, IsMaster
from src.apps.orders import cloudpayments
from .models import Order, OrderStatus, PaymentType
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
          // could be CARD or CASH
          'payment_type': 'CARD',
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
          'payment_type': 'CARD',
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
        return queryset.filter(client=self.request.user.client) \
            .order_by('-date')

    def get_serializer_class(self):
        if not self.request:
            # TODO this is a fucking bug of the schema generation module
            return OrderListSerializer

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
          'payment_type':'CASH',
          'time': '11:00',
          'status': 'CREATED/ACCEPTED/DONE',
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
    # TODO needed by swagger
    serializer_class = OrderListSerializer

    def delete(self, request, *args, **kwargs):
        """
        Cancels an order

        Response:

        204 No Content
        """
        return super().delete(request, *args, **kwargs)


class CompleteOrderView(generics.GenericAPIView):
    view_name = 'complete-order'
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated, IsMaster)
    # TODO needed by swagger
    serializer_class = OrderListSerializer

    def patch(self, request, *args, **kwargs):
        """
        Marks an order as done and completes the payment procedure.

        If the order is paid by card, calls CloudPayments API and
        confirms the transaction, meaning that money will be transferred
        to the 4hands2go account.

        Response:

        204 No Content
        """
        order = self.get_object()
        if order.payment_type == PaymentType.CARD:
            cloudpayments.confirm(order)
        order.status = OrderStatus.DONE
        return Response(status=status.HTTP_204_NO_CONTENT)
