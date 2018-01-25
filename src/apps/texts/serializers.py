from rest_framework import serializers

from src.apps.texts.models import Text


class TextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Text
        exclude = ('id',)
