from rest_framework import serializers

from src.apps.finances.models import TransactionEntry
from src.apps.masters.models import Master


class TEMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Master
        fields = ('id', 'first_name')


class TransactionEntrySerializer(serializers.ModelSerializer):
    master = TEMasterSerializer(read_only=True)

    # order is represented only by ID

    class Meta:
        model = TransactionEntry
        fields = '__all__'
