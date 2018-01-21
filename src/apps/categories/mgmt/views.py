from rest_framework import generics, mixins, parsers
from rest_framework.exceptions import NotFound

from src.apps.categories.mgmt.serializers import \
    CreateUpdateServiceCategorySerializer, CreateUpdateServiceSerializer, \
    CreateUpdateDisplayItemSerializer
from src.apps.categories.models import ServiceCategory, Service, DisplayItem
from src.apps.categories.serializers import ServiceCategorySerializer, \
    DisplayItemSerializer, ServiceSerializer
from src.apps.categories.views import CategoryListView, DisplayItemListView
from src.apps.core.permissions import IsAdmin


class MgmtListCreateServiceCategoryView(mixins.CreateModelMixin,
                                        CategoryListView):
    view_name = 'mgmt-create-service-category'
    serializer_class = ServiceCategorySerializer
    permission_classes = (IsAdmin,)
    queryset = ServiceCategory.objects.all()

    def get_parsers(self):
        if self.request.method == 'GET':
            return [parsers.JSONParser()]
        elif self.request.method == 'POST':
            return [parsers.MultiPartParser()]

    def get_serializer_class(self):
        if not self.request:
            # TODO this is a fucking bug of the schema generation module
            return ServiceCategorySerializer

        if self.request.method == 'GET':
            return ServiceCategorySerializer
        elif self.request.method == 'POST':
            return CreateUpdateServiceCategorySerializer

    def post(self, request, *args, **kwargs):
        """
        Creates a category.

        It's a multipart request.

        Input:

        ``` { 'name':'super', 'image':'multipart-image' } ```

        Response:

        201 Created
        """
        return super().create(request, *args, **kwargs)


class MgmtUpdateDeleteServiceCategoryView(mixins.UpdateModelMixin,
                                          mixins.DestroyModelMixin,
                                          mixins.RetrieveModelMixin,
                                          generics.GenericAPIView):
    view_name = 'mgmt-update-service-category'
    serializer_class = CreateUpdateServiceCategorySerializer
    permission_classes = (IsAdmin,)
    queryset = ServiceCategory.objects.all()

    def get_parsers(self):
        if self.request.method == 'DELETE':
            return [parsers.JSONParser()]
        elif self.request.method == 'PATCH':
            return [parsers.MultiPartParser()]

    def get_serializer_class(self):
        if not self.request:
            # TODO this is a fucking bug of the schema generation module
            return CreateUpdateServiceCategorySerializer

        if self.request.method == 'GET':
            return ServiceCategorySerializer
        else:
            return super().get_serializer_class()

    def get(self, request, *args, **kwargs):
        """
        Returns category details.

        Response:
        200 OK
        ```
        {
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
        }

        ```

        """
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        Updates a category.

        It's a multipart request.

        Input:

        ``` { 'name':'super', 'image':'multipart-image' } ```

        Response:

        200 OK
        """
        return super().partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Deletes a category.

        Response:

        204 No content
        """
        return super().destroy(request, *args, **kwargs)


class MgmtCreateServiceView(mixins.CreateModelMixin,
                            generics.GenericAPIView):
    view_name = 'mgmt-create-service'
    serializer_class = CreateUpdateServiceSerializer
    permission_classes = (IsAdmin,)
    queryset = ServiceCategory.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if not self.request:
            # TODO this is a fucking bug of the schema generation module
            return context

        context['category'] = self.get_object()
        return context

    def post(self, request, *args, **kwargs):
        """
        Creates a service.

        Input:

        ```
        {
          'name':'hey',
          'description':'sweetheart',
          'cost':100,
          'min_duration':30,
          'max_duration':60
        }
        ```

        Response:

        201 Created
        """
        return super().create(request, *args, **kwargs)


class MgmtUpdateDeleteServiceView(mixins.UpdateModelMixin,
                                  mixins.DestroyModelMixin,
                                  generics.GenericAPIView):
    view_name = 'mgmt-update-service'
    serializer_class = CreateUpdateServiceSerializer
    permission_classes = (IsAdmin,)
    queryset = ServiceCategory.objects.all()

    def get_object(self):
        category = super().get_object()
        service_id = self.kwargs['service_id']
        try:
            return category.services.get(pk=service_id)
        except Service.DoesNotExist as ex:
            raise NotFound(f'Service with id {service_id} is not found')

    def patch(self, request, *args, **kwargs):
        """
        Updates a service.

        Input:

        ```
        {
          'name':'hey',
          'description':'sweetheart',
          'cost':100,
          'min_duration':30,
          'max_duration':60
        }
        ```

        Response:

        200 Created
        """
        return super().partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Deletes a service.

        Response:

        204 No content
        """
        return super().destroy(request, *args, **kwargs)


class MgmtListCreateDisplayItemView(mixins.CreateModelMixin,
                                    DisplayItemListView):
    view_name = 'mgmt-create-display-item'
    serializer_class = DisplayItemSerializer
    permission_classes = (IsAdmin,)
    queryset = DisplayItem.objects.all()

    def get_parsers(self):
        if self.request.method == 'GET':
            return [parsers.JSONParser()]
        elif self.request.method == 'POST':
            return [parsers.MultiPartParser()]

    def get_serializer_class(self):
        if not self.request:
            # TODO this is a fucking bug of the schema generation module
            return DisplayItemSerializer

        if self.request.method == 'GET':
            return DisplayItemSerializer
        elif self.request.method == 'POST':
            return CreateUpdateDisplayItemSerializer

    def post(self, request, *args, **kwargs):
        """
        Creates a display item.

        It's a multipart request.

        Input:

        ```
        {
          'name':'super',
          'image':'multipart-image',
          'categories':'1,2,3',
          'special':{}
        }
        ```

        Response:

        201 Created
        """
        return super().create(request, *args, **kwargs)


class MgmtUpdateDeleteDisplayItemView(mixins.UpdateModelMixin,
                                      mixins.DestroyModelMixin,
                                      generics.GenericAPIView):
    view_name = 'mgmt-update-display-item'
    serializer_class = CreateUpdateDisplayItemSerializer
    permission_classes = (IsAdmin,)
    queryset = DisplayItem.objects.all()

    def get_parsers(self):
        if self.request.method == 'DELETE':
            return [parsers.JSONParser()]
        elif self.request.method == 'PATCH':
            return [parsers.MultiPartParser()]

    def patch(self, request, *args, **kwargs):
        """
        Updates a display item.

        It's a multipart request.

        Input:

        ```
        {
          'name':'super',
          'image':'multipart-image',
          'categories':'1,2,3',
          'special':{}
        }
        ```

        Response:

        200 OK
        """
        return super().partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Deletes a display item.

        Response:

        204 No content
        """
        return super().destroy(request, *args, **kwargs)


class MgmtServiceListView(generics.ListAPIView):
    view_name = 'service-list'

    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = (IsAdmin,)

    def get(self, request, *args, **kwargs):
        """
        Returns a list of all services.

        Response:
        200 OK
        ```
        [{
          'id':100,
          'name':'Slow and steady'
          'description':'Yeah!"
          'cost':100,
          'min_duration':30
          'max_duration':60,
          'category':{
            'id':300,
            'name':'super category',
            'image':'url-to-image'
          }
        }]
        ```

        """
        return super().get(request, *args, **kwargs)
