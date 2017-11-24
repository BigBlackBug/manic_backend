from urllib.parse import urlparse

from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse

from src.apps.clients.models import PaymentCard
from src.apps.core import utils as core_utils
from src.apps.core.permissions import IsClient
from . import cloudpayments
from .models import Order, CloudPaymentsTransaction
from .serializers import OrderListSerializer, CloudPaymentsTransactionSerializer


class PayForOrderView(generics.GenericAPIView):
    view_name = 'pay-for-order'
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    permission_classes = (IsAuthenticated, IsClient)

    def post(self, request, *args, **kwargs):
        """
        Charges the card `card_id` for the price of the order.

        IP address is required by the CloudPayments API

        Input:
        ```
        {
          'card_id': 100,
        }
        ```

        Response:

        201 Created - The card has been successfully charged.

        202 Accepted - The card requires 3D Secure auth. Check out
        CloudPayments docs for further info

        ```
        {
          //AcsUrl in CP docs
          'confirmation_url':''
          'params':{}
        }
        ```

        """
        # TODO add serializers for validation?
        card_id = request.data['card_id']
        ip_address = core_utils.get_ip_address(request)

        order = self.get_object()

        card = PaymentCard.objects.get(pk=card_id)
        if card not in request.user.client.payment_cards.all():
            raise ValidationError('Trying to use someone else\'s card')
        s3d_url = f'{reverse(FinishS3DView.view_name)}?order_id={order.id}'
        return cloudpayments.process_payment(card, order, ip_address,
                                             s3d_url)


class CloudPaymentsTransactionView(generics.RetrieveAPIView):
    view_name = 'cp-transaction-view'
    queryset = CloudPaymentsTransaction.objects.all()
    serializer_class = CloudPaymentsTransactionSerializer
    permission_classes = (IsAuthenticated, IsClient)
    lookup_field = 'transaction_id'

    def get(self, request, *args, **kwargs):
        """
        Returns an instance of CloudPaymentsTransaction

        Response:

        200 OK
        ```
        {
          "transaction_id": 500,
          "transaction_info": {
            //either an error description, or instance
            //of an internal transaction in CloudPayments system
          },
          "status": "CREATED/FINISHED/S3D_FAILED"
        }

        """
        return super().get(request, *args, **kwargs)


class FinishS3DView(generics.GenericAPIView):
    view_name = 'finish-s3d-view'
    # TODO swagger needs this
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    # this endpoint is a callback
    # so it should be accessible for everyone
    permission_classes = ()

    def post(self, request, *args, **kwargs):
        """
        A callback that finishes the 3D Secure authorization.
        No need to call it manually.
        """
        # these params will be here. no need to check for
        # existence or validity
        transaction_id = self.request.data['MD']
        pa_res = self.request.data['PaRes']
        order_id = self.request.query_params['order_id']
        order = Order.objects.get(pk=order_id)

        cloudpayments.finish_s3d(order, transaction_id, pa_res)
        return Response(status=status.HTTP_204_NO_CONTENT)
