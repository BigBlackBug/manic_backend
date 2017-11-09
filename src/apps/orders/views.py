from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from src.apps.core.permissions import IsClient, IsMaster, HasAccount
from src.apps.orders import cloudpayments, order_utils
from .models import Order, OrderStatus, PaymentType, OrderItem
from .serializers import OrderCreateSerializer, OrderListSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    view_name = 'order-list-create'
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated, HasAccount)

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
        # only clients may create orders
        if not request.user.is_client():
            raise PermissionDenied(detail=IsClient.message)
        return super().post(request, *args, **kwargs)

    def get_serializer_class(self):
        if not self.request:
            # TODO this is a fucking bug of the schema generation module
            return OrderListSerializer

        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderListSerializer

    def get_queryset(self):
        if self.request.user.is_master():
            order_items = OrderItem.objects.filter(
                master=self.request.user.master).select_related(
                'order').order_by('-order__date').all()
            orders = []
            for item in order_items:
                orders.append(item.order)
            return orders
        else:
            return Order.objects.filter(client=self.request.user.client) \
                .order_by('-date').all()

    def get(self, request, *args, **kwargs):
        """
        Returns a list of active and past orders
        of the current client or master ordered by date

        Response:

        200 OK
        ```
        {
          'active': [{
            'date': '2017-10-18',
            'payment_type':'CASH',
            'time': '11:00',
            'status': 'CREATED/ACCEPTED',
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
          }],
          'history':[{...'status':'DONE'...}]
        ```

        """

        active, history = order_utils.split_orders(self.get_queryset())

        return Response({
            'active': self.get_serializer(active, many=True).data,
            'history': self.get_serializer(history, many=True).data,
        })


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
