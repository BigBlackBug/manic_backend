from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter

from src.apps.core.permissions import IsAdmin
from src.apps.orders.models import Order
from ..serializers import OrderListSerializer


class OrderListView(generics.ListAPIView):
    view_name = 'mgmt-client-list'
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_fields = ('status', 'id')
    ordering = ('-date', 'time')

    def get(self, request, *args, **kwargs):
        """
        Returns a list of orders.

        Response:

        200 OK
        ```
        [{
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
          }
        }]
        ```

        """
        return super().get(request, *args, **kwargs)
