from rest_framework import generics, mixins, parsers
from rest_framework.exceptions import NotFound

from src.apps.categories.mgmt.serializers import \
    CreateUpdateServiceCategorySerializer, CreateUpdateServiceSerializer, \
    CreateUpdateDisplayItemSerializer
from src.apps.categories.models import ServiceCategory, Service, DisplayItem
from src.apps.categories.serializers import ServiceCategorySerializer, \
    DisplayItemSerializer
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
        return super().create(request, *args, **kwargs)


class MgmtUpdateDeleteServiceCategoryView(mixins.UpdateModelMixin,
                                          mixins.DestroyModelMixin,
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

    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
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
        return super().partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
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
        return super().partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
