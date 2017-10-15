from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from src.apps.categories.models import Service
from src.apps.masters.models import Master, TimeSlot
from .models import Order, OrderItem


class OrderItemSerializer(serializers.Serializer):
    master_id = serializers.IntegerField(min_value=0)
    service_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0)
    )


class OrderSerializer(serializers.Serializer):
    date = serializers.DateField(required=True)
    time = serializers.TimeField(required=True, format='%H:%M')
    order_items = OrderItemSerializer(many=True, required=True, write_only=True)
    # if an order is special, contains data for the 'special' order handler
    special = serializers.DictField(required=False)

    def create(self, validated_data):
        order_items = validated_data.pop('order_items')
        order = Order.objects.create(client=self.context['request'].user.client,
                                     **validated_data)

        for item in order_items:
            master = Master.objects.prefetch_related('schedule').get(pk=item['master_id'])
            services = Service.objects.filter(pk__in=item['service_ids'])
            if not services:
                raise ValidationError(f'services with provided ids:{item["service_ids"]} '
                                      f'are not found')
            schedule = master.get_schedule(validated_data['date'])
            order_item = None
            next_time = None
            for service in services:
                order_item = OrderItem.objects.create(order=order, master=master, service=service)
                next_time = schedule.assign_time(next_time or validated_data['time'],
                                                 int(service.max_duration / TimeSlot.DURATION),
                                                 order_item)
            # add +1 if it's not end of the day
            if next_time:
                schedule.assign_time(next_time, 1, order_item)
        return order
