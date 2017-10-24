from rest_framework import serializers

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


class ServiceCategorySerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceCategory
        fields = ('name', 'image', 'services')
        depth = 1


class DisplayItemSerializer(serializers.ModelSerializer):
    categories = ServiceCategorySerializer(many=True, read_only=True)
    special = serializers.DictField(required=False)

    class Meta:
        model = DisplayItem
        fields = ('name', 'categories', 'image', 'special')
