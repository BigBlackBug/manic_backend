import datetime

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from src.apps.categories.models import Service
from src.apps.categories.serializers import ServiceSerializer
from src.apps.core.serializers import LocationSerializer
from src.apps.masters import time_slot_utils
from .models import Master, Schedule, TimeSlot, Time, MasterStatus


class TimeSlotSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField('time_value')

    def time_value(self, time_slot: TimeSlot):
        # chopping off seconds
        return str(time_slot.time.value)[:-3]

    class Meta:
        model = TimeSlot
        fields = ('time', 'taken')


class ScheduleSerializer(serializers.ModelSerializer):
    time_slots = TimeSlotSerializer(many=True, read_only=True)

    class Meta:
        model = Schedule
        exclude = ('id', 'master')


class MasterSerializer(serializers.ModelSerializer):
    """
    Provides a complete representation of a master
    """

    class PortfolioImageField(serializers.RelatedField):
        def to_representation(self, instance):
            url = instance.image.url
            request = self.context.get('request', None)
            if request is not None:
                url = request.build_absolute_uri(url)
            return {
                'id': instance.id,
                'url': url,
                'description': instance.description,
                'status': instance.status,
            }

    location = LocationSerializer(read_only=True)
    services = ServiceSerializer(many=True, read_only=True)
    schedule = ScheduleSerializer(many=True, read_only=True)
    portfolio = PortfolioImageField(many=True, read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)

    class Meta:
        model = Master
        exclude = ('user',)


class MasterScheduleSerializer(serializers.BaseSerializer):
    """
    Given a master instance, serializes only his schedule to a list
    """

    def to_representation(self, instance: Master):
        return ScheduleSerializer(instance.schedule, many=True,
                                  read_only=True).data


class SimpleMasterSerializer(serializers.ModelSerializer):
    """
    Provides a short representation of a master, to be used in the
    main list of masters
    """
    DISTANCE_NOT_AVAILABLE = -1

    services = ServiceSerializer(many=True, read_only=True)
    location = LocationSerializer(read_only=True)
    distance = serializers.SerializerMethodField('_distance', read_only=True)

    available_slots = serializers.SerializerMethodField('_available_slots',
                                                        read_only=True)

    def _distance(self, master: Master):
        coordinates = self.context.get('coordinates')
        if not coordinates:
            return self.DISTANCE_NOT_AVAILABLE
        else:
            return master.distance(*coordinates)

    def _available_slots(self, master: Master):
        return self.context.get('available_slots', {}).get(master.id, [])

    class Meta:
        model = Master
        fields = ('id', 'about', 'first_name', 'avatar', 'services',
                  'location', 'distance', 'available_slots')


class CreateScheduleSerializer(serializers.ModelSerializer):
    time_slots = serializers.CharField(write_only=True)
    date = serializers.DateField(write_only=True)

    def create(self, validated_data):
        master = self.context['request'].user.master
        # Schedule.objects.get(master=master, )
        schedule, created = Schedule.objects.get_or_create(
            master=master, date=validated_data['date'],
        )
        time_tuples = time_slot_utils.parse_time_slots(
            validated_data['time_slots'], include_last=True)
        # TODO that's not fool proof
        # timeslots may not be overwritten

        for time_tuple in time_tuples:
            TimeSlot.objects.create(
                time=Time.objects.create(hour=time_tuple.hour,
                                         minute=time_tuple.minute),
                schedule=schedule,
                taken=False)
        return schedule

    def validate_date(self, date_value):
        if date_value > (timezone.now() +
                             datetime.timedelta(days=14)).date():
            raise ValidationError(detail='You may not create schedules '
                                         'that are more than two weeks '
                                         'away from today')
        return date_value

    def validate_time_slots(self, time_slots):
        # TODO verify time_slots
        return time_slots

    class Meta:
        model = Schedule
        fields = ('time_slots', 'date')


class MasterCreateSerializer(serializers.ModelSerializer):
    services = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        required=True, write_only=True)

    def create(self, validated_data):
        services = validated_data.pop('services', [])
        master = Master.objects.create(user=self.context['request'].user,
                                       status=MasterStatus.ON_REVIEW,
                                       **validated_data)
        for service in services:
            master.services.add(Service.objects.get(pk=service))
        master.save()
        return master

    class Meta:
        model = Master
        fields = ('first_name', 'gender', 'date_of_birth',
                  'email', 'about', 'services')
