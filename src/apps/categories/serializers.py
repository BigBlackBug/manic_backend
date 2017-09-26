from rest_framework import serializers

from .models import ServiceCategory, Service


class SimpleServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ('name', 'image', 'id')


class ServiceSerializer(serializers.ModelSerializer):
    category = SimpleServiceCategorySerializer()

    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ('category', 'name', 'description', 'duration', 'cost')


class ServiceCategorySerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceCategory
        fields = ('name', 'image', 'services')
        depth = 1
