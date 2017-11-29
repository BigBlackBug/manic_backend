from rest_framework import serializers

from .models import Location


class ImageSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True, write_only=True)


class DescriptionImageSerializer(serializers.Serializer):
    image_id = serializers.IntegerField(required=True, write_only=True)
    description = serializers.CharField(max_length=1024, required=False,
                                        write_only=True)
    status = serializers.CharField(max_length=13, write_only=True,
                                   required=False)


class ImageListSerializer(serializers.Serializer):
    images = serializers.ListField(child=serializers.ImageField(
        required=True, allow_empty_file=False), required=True)


class LocationSerializer(serializers.ModelSerializer):
    # TODO both fields are required
    class Meta:
        model = Location
        exclude = ('id',)
