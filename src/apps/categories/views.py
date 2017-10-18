from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from .models import DisplayItem
from .serializers import DisplayItemSerializer


class DisplayItemList(generics.ListAPIView):
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
        {
          'name':'Super Service',
          'image':'url-to-image',
          'categories':[{
            'name':'category one',
            'image':'url-to-image',
            'services':[{
                'id':100,
                'name':'Service'
                'description':'Yeah!"
                'cost':100,
                'min_duration':30
                'max_duration':60
            }]
          }],
          //attributes of a special order
          'special':{
            'type':'',
            ...
          }
        }
        ```

        """
        return super().get(request, *args, **kwargs)
