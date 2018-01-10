from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import generics, status, mixins
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from src.apps.core.permissions import IsClient, IsMaster
from src.apps.orders import cloudpayments, order_utils, notifications
from .models import Order, OrderStatus, PaymentType, OrderItem
from .serializers import OrderCreateSerializer, OrderListSerializer, \
    OrderUpdateSerializer


class OrderListCreateView(generics.ListCreateAPIView):
    view_name = 'order-list-create'
    queryset = Order.objects.all()
    # TODO isactivated
    permission_classes = (IsAuthenticated,)

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
            'locked': false,
            'master_id': 10,
            'service_ids': [25]
          }, {
            'locked': false,
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
            'locked': true,
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
        if not request.user.is_client(request):
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
        if self.request.user.is_master(self.request):
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
            'id': 100500,
            'date': '2017-10-18',
            'payment_type':'CASH',
            'time': '11:00',
            'status': 'ACCEPTED/STARTED/DONE',
            'special': {},
            'comment': '',
            'order_items': [{
              'service': {
                  'name': 'super service',
                  'cost': 100,
                  'min_duration': 30,
                  'max_duration': 60,
                  'category':{
                    'name': 'super category'
                  }
              },
              'client':{
                'id':42,
                'avatar':'link-to-img',
                'first_name':'Johnny',
                'phone':'88005553535',
                'home_address':{**Address** model}
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


class OrderUpdateCommentView(mixins.UpdateModelMixin, generics.GenericAPIView):
    view_name = 'update-order-comment'
    queryset = Order.objects.all()
    permission_classes = (IsClient,)
    # used by patch
    serializer_class = OrderUpdateSerializer

    def patch(self, request, *args, **kwargs):
        """
        Creates or updates an order's comment.
        Can only be called by a client on orders that are DONE

        Input:
        ```
        {
          'comment': 'I liked it!'
        }
        ```

        Response:

        200 OK

        403 Forbidden - if the order is not DONE
        """
        # only clients can update orders
        # TODO that's is not true, but good enough at the moment
        return self.partial_update(request, *args, **kwargs)


class OrderCancelView(mixins.DestroyModelMixin,
                      generics.GenericAPIView):
    view_name = 'cancel-order'
    queryset = Order.objects.all()
    # TODO isactivated
    permission_classes = (IsAuthenticated,)
    # used by patch
    serializer_class = OrderUpdateSerializer

    def delete(self, request, *args, **kwargs):
        """
        Cancels an order.

        If called by a master, only the respective OrderItem
        is deleted and a new master is assigned to the order
        for the same service, unless the OrderItem is locked.

        If called by a client, the order itself is deleted.

        An order may be canceled not more than 3 hours before the deadline.

        Response:

        204 No Content

        403 Forbidden - If you are trying to delete someone
        else's order, or you're too late, or the order is locked
        """
        order = self.get_object()

        order_date = timezone.make_aware(
            datetime.combine(order.date, order.time))
        if order_date - timezone.now() < \
                timedelta(hours=settings.ORDER_CANCELLATION_WINDOW_HOURS):
            raise PermissionDenied(detail='You may not delete orders '
                                          'less than 3 hours before '
                                          'the deadline')

        if request.user.is_client(request):
            # check is the order belongs to the client
            if order.client == request.user.client:
                # since order is canceled
                # the master should not rely on that money
                for order_item in order.order_items.all():
                    order_item.master.add_future_balance(
                        -1 * order_item.service.cost *
                            order.client.tip_multiplier())
                order.delete()
            else:
                raise PermissionDenied(detail="You are not allowed to cancel"
                                              "someone else's order")
        else:
            order_items = order.order_items.filter(master=request.user.master) \
                .all()
            if len(order_items) == 0:
                raise PermissionDenied(detail='You are not responsible '
                                              'for this order')
            for order_item in order_items:
                if order_item.locked:
                    raise PermissionDenied(detail='You are not allowed '
                                                  'to cancel a locked order')
                # since order is canceled
                # the master should not rely on that money
                order_item.master.add_future_balance(
                    -1 * order_item.service.cost * order.client.tip_multiplier())
                order_item.delete()
                # TODO start looking for a new master
                # TODO add push notification to client
                if len(order.order_items.all()) == 0:
                    # it makes sense to delete the order if there was
                    # only one order item
                    order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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

        200 OK
        ```
        {
          //cloudpayments transaction id. null, in case the order
          //is paid by cash
          'transaction_id: 100500
        }
        ```
        """
        order = self.get_object()
        if order.status != OrderStatus.STARTED:
            raise ValidationError("Order must be STARTED by the master")
        if order.payment_type == PaymentType.CARD:
            cloudpayments.confirm_payment(order.transaction, order.total_cost)

        # only one master of the order can complete the order
        order.complete()
        order.save()

        if order.client.device:
            order.client.device.send_message(
                notifications.ORDER_COMPLETE_TITLE,
                notifications.ORDER_COMPLETE_CONTENT(
                    order.time.strftime('%H:%M')),
                data={
                    "order_id": order.id
                })
        return Response(status=status.HTTP_200_OK, data={
            'transaction_id': order.transaction and
                              order.transaction.transaction_id
        })


class StartOrderView(generics.GenericAPIView):
    view_name = 'start-order'
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated, IsMaster)
    # TODO needed by swagger
    serializer_class = OrderListSerializer

    def patch(self, request, *args, **kwargs):
        """
        Marks an order as started.

        Response:

        204 No Content
        """
        order = self.get_object()
        if order.status != OrderStatus.ACCEPTED:
            raise ValidationError("Order must be ACCEPTED by the master")

        order.start()
        order.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
