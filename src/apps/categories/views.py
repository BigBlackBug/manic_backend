# Create your views here.
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import ServiceCategory
from .serializers import ServiceCategorySerializer


class ServiceCategoryList(generics.ListAPIView):
    view_name = 'service-category-list'

    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = (IsAuthenticated,)
