from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from src.apps.categories.models import Service
from src.apps.clients.serializers import OrderClientSerializer
from src.apps.masters.models import Master, TimeSlot
from src.apps.orders import notifications
from .models import Order, OrderItem, PaymentType, CloudPaymentsTransaction, \
    OrderStatus


# out
class OrderItemListSerializer(serializers.BaseSerializer):
    def to_representation(self, obj: OrderItem):
        request = self.context.get('request', None)

        avatar_url = obj.master.avatar.url
        if request:
            avatar_url = request.build_absolute_uri(avatar_url)

        return {
            'service': {
                'category': {
                    'name': obj.service.category.name,
                },
                'min_duration': obj.service.min_duration,
                'max_duration': obj.service.max_duration,
                'name': obj.service.name,
                'cost': obj.service.cost
            },
            'master': {
                'first_name': obj.master.first_name,
                'avatar': avatar_url
            },
            'locked': obj.locked
        }


# in
class OrderItemCreateSerializer(serializers.Serializer):
    master_id = serializers.IntegerField(min_value=0)
    service_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=0)
    )
    locked = serializers.BooleanField(required=True)


# out
class OrderListSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    client = OrderClientSerializer(read_only=True)
    date = serializers.DateField(read_only=True)
    time = serializers.TimeField(read_only=True, format='%H:%M')
    order_items = OrderItemListSerializer(many=True, read_only=True)
    special = serializers.DictField(read_only=True)
    payment_type = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)


# in
class OrderCreateSerializer(serializers.Serializer):
    # because the POST method should return certain fields
    id = serializers.IntegerField(read_only=True)
    date = serializers.DateField()
    time = serializers.TimeField(format='%H:%M')
    order_items = OrderItemCreateSerializer(many=True, write_only=True)
    # if an order is special, contains data for the 'special' order handler
    special = serializers.DictField(required=False)
    payment_type = serializers.ChoiceField(choices=PaymentType.CHOICES)

    def create(self, validated_data):
        order_items = validated_data.pop('order_items')
        client = self.context['request'].user.client
        order = Order.objects.create(client=client, **validated_data)

        for item in order_items:
            master = Master.objects.prefetch_related('schedule').get(
                pk=item['master_id'])
            services = Service.objects.filter(pk__in=item['service_ids'])
            if not services:
                raise ValidationError(
                    f'services with provided ids:{item["service_ids"]} '
                    f'are not found')
            schedule = master.get_schedule(validated_data['date'])
            order_item = None
            next_time = None
            for service in services:
                order_item = OrderItem.objects.create(order=order,
                                                      master=master,
                                                      service=service,
                                                      locked=item['locked'])

                master.create_order_payment(service, client.tip_multiplier(),
                                            order.payment_type)
                next_time = schedule.assign_time(
                    next_time or validated_data['time'],
                    int(service.max_duration / TimeSlot.DURATION),
                    order_item)
            # add +1 if it's not end of the day
            if next_time:
                schedule.assign_time(next_time, number_of_slots=1,
                                     order_item=order_item)
            if master.device:
                master.device.send_message(
                    notifications.NEW_ORDER_TITLE,
                    notifications.NEW_ORDER_CONTENT(
                        order_time=order.time.strftime('%H:%M'),
                        order_date=order.date.strftime('%Y-%m-%d')),
                    data={
                        'event': notifications.NEW_ORDER_EVENT
                    })
        return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    comment = serializers.CharField(max_length=1024, write_only=True)

    def update(self, instance, validated_data):
        if 'comment' in validated_data:
            if instance.status != OrderStatus.DONE:
                raise PermissionDenied(
                    detail="You are not allowed to add a comment "
                           "to an order that is not DONE")
        return super().update(instance, validated_data)

    class Meta:
        model = Order
        fields = ('comment',)


class CloudPaymentsTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CloudPaymentsTransaction
        exclude = ('id',)
