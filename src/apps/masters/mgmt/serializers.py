from rest_framework import serializers

from ..models import Master
from ..serializers import BalanceSerializer, MasterUpdateSerializer


class MgmtMasterListSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source='user.phone')
    balance = BalanceSerializer()

    class Meta:
        model = Master
        fields = ('id', 'first_name', 'phone', 'email', 'balance', 'status')
        read_only_fields = fields


class MgmtMasterUpdateSerializer(MasterUpdateSerializer):
    class Meta(MasterUpdateSerializer.Meta):
        fields = [*MasterUpdateSerializer.Meta.fields,'status']
