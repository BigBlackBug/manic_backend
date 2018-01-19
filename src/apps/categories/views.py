from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from src.apps.masters import master_utils
from src.apps.masters.time_slot_utils import add_time
from .models import DisplayItem, ServiceCategory, Service
from .serializers import DisplayItemSerializer, ServiceCategorySerializer, \
    RecommendationInputSerializer


class DisplayItemListView(generics.ListAPIView):
    view_name = 'display-item-list'

    queryset = DisplayItem.objects.all()
    serializer_class = DisplayItemSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request, *args, **kwargs):
        """
        Returns a list of all DisplayItems. These are wrappers
        around service categories, which can contain several categories
        and describe **special** types of orders

        Response:
        200 OK
        ```
        [{
          //Optional
          'name':'Four hands special',
          //Optional
          'image':'url-to-item-image',
          'categories':[{
            'id': 500,
            'name':'Hand Job',
            'image':'url-to-image',
            'services':[{
              'id':100,
              'name':'Slow and steady'
              'description':'Yeah!"
              'cost':100,
              'min_duration':30
              'max_duration':60
            }]
          },{
            'id': 700,
            'name':'Foot Job',
            'image':'url-to-image',
            'services':[{
              'id':100,
              'name':'Extra tender'
              'description':'Oh Yeah!"
              'cost':500,
              'min_duration':30
              'max_duration':60
            }]
          }],
          //attributes of a special order
          'special':{
            'type':'composite',
            ...
          }
        },
        {
          'categories':[{
            'id': 800,
            'name':'Hand Job',
            'image':'url-to-image',
            'services':[{
              'id':100,
              'name':'Slow and steady'
              'description':'Yeah!"
              'cost':100,
              'min_duration':30
              'max_duration':60
            }]
          }]
        }]
        ```

        """
        return super().get(request, *args, **kwargs)


class CategoryListView(generics.ListAPIView):
    view_name = 'category-list'

    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request, *args, **kwargs):
        """
        Returns a list of all categories.

        Response:
        200 OK
        ```
        [{
            'id': 800,
            'name':'Hand Job',
            'image':'url-to-image',
            'services':[{
              'id':100,
              'name':'Slow and steady'
              'description':'Yeah!"
              'cost':100,
              'min_duration':30
              'max_duration':60
            }]
          }]
        }]
        ```

        """
        return super().get(request, *args, **kwargs)


class UpsaleRecommendationsView(views.APIView):
    view_name = 'upsale-recommendations'

    def post(self, request, *args, **kwargs):
        """
        Returns possible upsale options with respect
        to the provided order configuration

        Input:

        ```
        {
          'date': '2017-10-18',
          'time': '11:00',
          'order_items': [{
            'master_id': 11,
            'service_ids': [25]
          }, {
            'master_id': 11,
            'service_ids': [16]
          }]
        }
        ```

        Response:

        200 OK

        ```
        [{
          'master_id': 10,
          'service_id': 50
        }]
        ```
        """
        serializer = RecommendationInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_date = serializer.validated_data['date']
        order_time = serializer.validated_data['time']
        order_items = serializer.validated_data['order_items']

        for item in order_items:
            # expected service execution start time
            item['time'] = add_time(
                source_time=order_time,
                minutes=sum(
                    [service.max_duration for service in
                     Service.objects.filter(pk__in=item['service_ids'])]))

        result = master_utils.upsale_search(order_items, order_date)
        return Response(data=result)
