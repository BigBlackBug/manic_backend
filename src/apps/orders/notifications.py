NEW_ORDER_TITLE = "Новый заказ"
ORDER_COMPLETE_TITLE = "Заказ завершён"


def ORDER_COMPLETE_CONTENT(order_time):
    return f'Запись на {order_time} завершена. Оцените работу мастера'


def NEW_ORDER_CONTENT(order_time, order_date):
    return f'У Вас новая запись на {order_time}, {order_date}'
