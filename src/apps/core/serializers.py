from rest_framework import serializers

from .models import Location


class ImageSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True, write_only=True)


class DescriptionImageSerializer(serializers.Serializer):
    image = serializers.ImageField(required=True, write_only=True)
    description = serializers.CharField(max_length=1024,
                                        required=True, write_only=True)


# class ListImageSerializer(serializers.Serializer):
#     images = serializers.ListField(child=
#                                    DescriptionImageField(), required=True,
#                                    write_only=True)


class LocationSerializer(serializers.ModelSerializer):
    # TODO both fields are required
    class Meta:
        model = Location
        exclude = ('id',)
