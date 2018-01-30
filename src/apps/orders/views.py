import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import generics, status, mixins
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from src.apps.core.exceptions import ApplicationError
from src.apps.core.permissions import IsClient, IsMaster
from src.apps.masters.models import TimeSlot
from src.apps.orders import cloudpayments, order_utils, notifications
from .models import Order, OrderStatus, PaymentType, OrderItem
from .serializers import OrderCreateSerializer, OrderListSerializer, \
    OrderUpdateSerializer

logger = logging.getLogger(__name__)


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
          'comment': 'Make it quick!',
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
                'order').order_by('order__date',
                                  'order__time').all()
            orders = set()
            for item in order_items:
                orders.add(item.order)
            return orders
        else:
            return Order.objects.filter(client=self.request.user.client) \
                .order_by('date', 'time').all()

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
            'status': 'CREATED/ACTIVATED/STARTED/DONE',
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
                  'id': 100,
                  'first_name': 'Vasya',
                  'avatar': 'url-to-avatar'
              }]
          }],
          'history':[{...'status':'DONE'...}]
        ```

        """

        active, history = order_utils.split_orders(
            self.get_queryset())

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

        OK - replacement is found, FAILURE - replacement was not found
        ``` {'result':'OK/FAILURE'} ```

        403 Forbidden - If you are trying to delete someone
        else's order, or you're too late, or the order is locked
        """
        order = self.get_object()
        # TODO will break in case of multiple timezones
        order_date = datetime.combine(order.date, order.time)
        if order_date - timezone.now() < \
                timedelta(hours=settings.ORDER_CANCELLATION_WINDOW_HOURS):
            raise PermissionDenied(detail='You may not delete orders '
                                          'less than 3 hours before '
                                          'the deadline')
        response_status = 'OK'

        if request.user.is_client(request):
            # check is the order belongs to the client
            if order.client == request.user.client:
                logger.info(
                    f'Cancelling order {order.id} initiated by '
                    f'client {order.client.id}')
                # since order is canceled
                # the master should not rely on that money
                for order_item in order.order_items.all():
                    order_item.master.cancel_order_payment(order, order_item)
                    slots = TimeSlot.objects.filter(order_item=order_item)
                    for slot in slots:
                        slot.taken = False
                        slot.save()
                order.delete()
            else:
                raise PermissionDenied(detail="You are not allowed to cancel"
                                              "someone else's order")
        else:
            master = request.user.master
            logger.info(
                f'Cancelling order {order.id} initiated by master'
                f' {master.first_name}')
            # converting to a list because I might delete the order
            # and I don't want dependency induced crashes
            order_items = list(order.order_items
                               .filter(master=master).all())
            if len(order_items) == 0:
                raise PermissionDenied(detail='You are not responsible '
                                              'for this order')
            success = order_utils.find_replacement_masters(
                order, order_items, master)
            if not success:
                response_status = 'FAILURE'

        return Response(status=status.HTTP_204_NO_CONTENT, data={
            'result': response_status
        })


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
        logger.info(f'Completing order {order.id}')

        if order.status != OrderStatus.STARTED:
            raise ValidationError("Order must be STARTED by the master")
        if order.payment_type == PaymentType.CARD:
            logger.info(f'Payment type of order {order.id} is CARD. '
                        f'Confirming payment with '
                        f'transaction {order.transaction.transaction_id}')
            cloudpayments.confirm_payment(order.transaction, order.total_cost)

        # only one master of the order can complete the order
        order.complete()
        order.save()

        if order.client.device:
            logger.info(f'Sending ORDER_COMPLETE notification to '
                        f'client {order.client.first_name}, '
                        f'order_id={order.id}')
            order.client.device.send_message(
                notifications.ORDER_COMPLETE_TITLE,
                notifications.ORDER_COMPLETE_CONTENT(
                    order.time.strftime('%H:%M')),
                data={
                    'order_id': order.id,
                    'event': notifications.ORDER_COMPLETE_EVENT
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
        if order.status != OrderStatus.ACTIVATED:
            raise ValidationError("Order must be ACTIVATED by the master")
        now = timezone.now()

        if order.date != now.date():
            raise ApplicationError(
                error_type=ApplicationError.ErrorTypes.ORDER_START_WRONG_DAY)

        order_date = datetime.combine(order.date, order.time)
        if order_date - now > \
                timedelta(minutes=settings.ORDER_START_WINDOW_MINUTES):
            raise ApplicationError(
                error_type=ApplicationError.ErrorTypes.ORDER_START_TOO_EARLY)

        order.start()
        order.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
