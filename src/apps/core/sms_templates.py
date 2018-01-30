def REGISTRATION_TEMPLATE(code: str):
    return f'Доброго времени суток! Ваш код активации: {code}'


def NEW_ORDER_TEMPLATE(order, masters):
    masters = list(masters)
    if len(masters) == 1:
        return f'У Вас новая запись на {order.time}, {order.date}. ' \
               f'К вам приедет мастер: {masters[0].first_name}. ' \
               f'К оплате {order.total_cost}.'
    elif len(masters) > 1:
        return f'У Вас новая запись на {order.time}, {order.date}. ' \
               f'К вам приедут мастера: ' \
               f'{[master.first_name for master in masters]}. ' \
               f'К оплате {order.total_cost}.'