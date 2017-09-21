from rest_framework import serializers

from .models import ServiceCategory, Service


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ('category', 'name', 'description', 'duration', 'cost')


class ServiceCategorySerializer(serializers.ModelSerializer):
    # image = serializers.ImageField(read_only=True)
    # name = serializers.CharField(max_length=64, read_only=True)
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceCategory
        fields = ('name', 'image', 'services')
