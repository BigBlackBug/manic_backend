NEW_ORDER_TITLE = "Новый заказ"
NEW_ORDER_EVENT = 'NEW_ORDER'

ORDER_COMPLETE_TITLE = "Заказ завершён"
ORDER_COMPLETE_EVENT = 'ORDER_COMPLETE'


def ORDER_COMPLETE_CONTENT(order_time):
    return f'Запись на {order_time} завершена. Оцените работу мастера'


def NEW_ORDER_CONTENT(order_time, order_date, client_name):
    return f'У Вас новая запись на {order_time}, {order_date} ' \
           f'к клиенту {client_name}'
