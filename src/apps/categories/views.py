from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from .models import DisplayItem, ServiceCategory, Service
from .serializers import DisplayItemSerializer, ServiceCategorySerializer, \
    ServiceSerializer


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


