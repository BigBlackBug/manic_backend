from typing import Iterable

from rest_framework.exceptions import PermissionDenied

from src.apps.masters import master_utils
from src.apps.masters.filtering import FilteringParams, FilteringFunctions
from src.apps.masters.models import Master
from src.apps.orders.models import Order, OrderStatus, OrderItem


def split_orders(orders: Iterable[Order]):
    """
    Splits the `order` list into two lists according to their status
    (DONE goes history, all others go active)

    :param orders:
    :return: two lists active, history
    """
    active = []
    history = []
    for order in orders:
        if order.status == OrderStatus.DONE:
            history.append(order)
        else:
            active.append(order)
    return active, history


def _find_replacement_master(order: Order, order_item: OrderItem,
                            old_master: Master):
    """
    Tries to assign a replacement master to the `order_item` of the `order`

    :return: replacement `Master` or None
    """
    order_service_id = order_item.service.id
    # since order is canceled
    # the master should not rely on that money
    client = order.client

    # looking for a replacement
    location = client.home_address.location
    params = FilteringParams({
        'service': order_service_id,
        'date': str(order.date),
        'time': order.time.strftime('%H:%M'),
        'coordinates': f'{location.lat},{location.lon}'
    }, client=client)

    masters, slots = master_utils.search(
        params, FilteringFunctions.datetime)

    if len(masters) == 0:
        # unable to find replacement
        # TODO add push notification to client and other masters
        return None

    masters = master_utils.sort_masters(masters, params.coordinates,
                                        params.distance)
    # we can't pick the same master
    masters = list(filter(lambda m: m.id != old_master.id, masters))
    if len(masters) == 0:
        # if the old master is the only one who fits
        # TODO add push notification to client and other masters
        return None

    return masters[0]


def find_replacement_masters(order, order_items, old_master):
    """
    Tries to find replacement masters for the `old_master`
    in all `order_items` in the `order`

    :return: True if masters in all `order_items` were successfully replaced
    """
    holder = []

    for order_item in order_items:
        if order_item.locked:
            raise PermissionDenied(detail='You are not allowed '
                                          'to cancel a locked order')
        replacement = _find_replacement_master(order, order_item, old_master)

        if replacement:
            holder.append((order, order_item, replacement))
        else:
            # at least one replacement not found, drop the order
            order.delete()
            return False

    # no breaks, recalculate the balance
    for order, order_item, replacement in holder:
        # this money is not yours anymore
        order_item.master.cancel_order_payment(order, order_item)

        # it's for the new guy
        replacement.create_order_payment(order, order_item)

        order_item.master = replacement
        order_item.save()
    return True
