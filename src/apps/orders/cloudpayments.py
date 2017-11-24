import json
from urllib import parse

from cloudpayments import CloudPayments, Currency, Transaction, Secure3d, \
    CloudPaymentsError, PaymentError
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from src.apps.clients.models import PaymentCard
from .models import Order, CloudPaymentsTransaction, CPTransactionStatus

client = CloudPayments(settings.CLOUDPAYMENTS_PUBLIC_ID,
                       settings.CLOUDPAYMENTS_API_SECRET)


def process_payment(card: PaymentCard, order: Order,
                    ip_address: str, confirmation_url):
    """
    Charges `card` with required amount, taken from `order.total_cost`

    :param card:
    :param order:
    :param ip_address:
    :param confirmation_url:
    :return: Response objects, with status 201 (charge successful,
    no confirmation required) or 202 (Secure 3D confirmation required)
    """
    response = client.charge_card(cryptogram=card.cryptogram,
                                  amount=order.total_cost,
                                  currency=Currency.RUB,
                                  name=card.client_name_on_card,
                                  ip_address=ip_address,
                                  require_confirmation=True)
    if isinstance(response, Transaction):
        # card doesn't support 3ds secure
        # transaction is created and is waiting
        # for confirmation
        order.transaction = CloudPaymentsTransaction.objects.create(
            transaction_id=response.id,
            transaction_info=response.__dict__)
        order.save()
        return Response(status=status.HTTP_201_CREATED)
    elif isinstance(response, Secure3d):
        # a client should send a POST there with specified params
        args = parse.urlencode({'order_id': order.id})
        params = response.redirect_params(
            term_url=f'{confirmation_url}?{args}')
        return Response(status=status.HTTP_202_ACCEPTED,
                        data={'confirmation_url': response.acs_url,
                              'params': params})


def finish_s3d(order: Order, transaction_id, pa_res):
    """
    Finished the transaction with `transaction_id` and adds a
    transaction to the `order`

    :param transaction_id:
    :param order:
    :param pa_res: required by the cloudpayments API
    """
    try:
        transaction = client.finish_3d_secure_authentication(transaction_id,
                                                             pa_res)
    except PaymentError as err:
        order.transaction = CloudPaymentsTransaction.objects.create(
            transaction_id=transaction_id,
            transaction_info=json.dumps(err.__dict__),
            status=CPTransactionStatus.S3D_FAILED)
    else:
        order.transaction = CloudPaymentsTransaction.objects.create(
            transaction_id=transaction.id,
            transaction_info=json.dumps(transaction.__dict__))


def confirm(order: Order):
    """
    Confirm payment of the order, after it is completed

    :raises CloudPaymentsError
    """
    transaction_id = order.transaction.transaction_id
    amount = order.total_cost
    client.confirm_payment(transaction_id, amount)
    order.transaction.confirm()
    order.transaction.save()
