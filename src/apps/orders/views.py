from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from src.apps.core.permissions import IsClient
from .models import Order
from .serializers import OrderSerializer


class OrderCreateView(generics.CreateAPIView):
    view_name = 'order-create'
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated, IsClient)
    serializer_class = OrderSerializer
