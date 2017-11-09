from typing import Iterable

from src.apps.orders.models import Order, OrderStatus


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
