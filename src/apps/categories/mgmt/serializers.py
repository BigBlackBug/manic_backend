from rest_framework import serializers

from src.apps.categories.models import ServiceCategory, Service, DisplayItem
from src.apps.masters.serializers import IdListField


# TODO get rid of get_fields, return id
class CreateUpdateServiceCategorySerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        for field in fields.values():
            field.required = True
        return fields

    class Meta:
        model = ServiceCategory
        fields = ('name', 'image',)


class CreateUpdateServiceSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        category = self.context['category']
        return Service.objects.create(category=category, **validated_data)

    # only for creation
    def get_fields(self):
        fields = super().get_fields()
        for field in fields.values():
            field.required = True
        return fields

    class Meta:
        model = Service
        fields = ('name', 'description', 'cost', 'min_duration', 'max_duration')


class CreateUpdateDisplayItemSerializer(serializers.ModelSerializer):
    categories = IdListField(required=True, write_only=True)
    special = serializers.DictField(required=False)
    name = serializers.CharField(max_length=64, required=False)
    image = serializers.ImageField(required=False)

    def create(self, validated_data):
        categories = validated_data.pop('categories', [])
        item = DisplayItem.objects.create(**validated_data)

        for category in categories:
            item.categories.add(ServiceCategory.objects.get(pk=category))

        item.save()
        return item

    def update(self, instance, validated_data):
        new_categories = validated_data.pop('categories', [])
        if new_categories:
            instance.categories = [ServiceCategory.objects.get(pk=category) for
                                   category in new_categories]
        return super().update(instance, validated_data)

    class Meta:
        model = DisplayItem
        fields = ('id', 'name', 'image', 'categories', 'special')
