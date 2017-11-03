from rest_framework import serializers

from src.apps.core.mixins import FilterEmptyFieldsMixin
from .models import ServiceCategory, Service, DisplayItem


class SimpleServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ('name', 'image', 'id')


class ServiceSerializer(serializers.ModelSerializer):
    category = SimpleServiceCategorySerializer()

    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ('category', 'name', 'description',
                            'min_duration', 'max_duration', 'cost')


class SimpleServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'name', 'description',
                  'min_duration', 'max_duration', 'cost')


class ServiceCategorySerializer(serializers.ModelSerializer):
    services = SimpleServiceSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceCategory
        fields = ('id', 'name', 'image', 'services')
        depth = 1


class DisplayItemSerializer(FilterEmptyFieldsMixin,
                            serializers.ModelSerializer):
    categories = ServiceCategorySerializer(many=True, read_only=True)
    special = serializers.DictField(required=False)

    class Meta:
        model = DisplayItem
        fields = ('name', 'categories', 'image', 'special')
