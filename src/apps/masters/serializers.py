import datetime
import time
from collections import namedtuple

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from src.apps.categories.serializers import ServiceSerializer
from src.apps.core.serializers import LocationSerializer
from .models import Master, Schedule, TimeSlot, Time


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
                return request.build_absolute_uri(url)
            return url

    location = LocationSerializer(read_only=True)
    services = ServiceSerializer(many=True, read_only=True)
    schedule = ScheduleSerializer(many=True, read_only=True)
    portfolio = PortfolioImageField(many=True, read_only=True)

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


TimeTuple = namedtuple('TimeTuple', ['hour', 'minute'])


class CreateScheduleSerializer(serializers.ModelSerializer):
    time_slots = serializers.CharField(write_only=True)
    date = serializers.DateField(write_only=True)

    def create(self, validated_data):
        master = self.context['request'].user.master
        # Schedule.objects.get(master=master, )
        schedule, created = Schedule.objects.get_or_create(
            master=master, date=validated_data['date'],
        )
        time_tuples = self._parse_time_slots(validated_data['time_slots'])
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

    def _parse_time_slots(self, slots_str: str):
        """
        Parses a string formatted like '10:00,13:00-15:00'
        The last time_slot is not created, i.e. in this case the last
        created slot will be at 14:30.
        Duplicates are counted once

        :param slots_str: source string
        :return: list of TimeTuple instances
        """
        result = set()
        pieces = slots_str.split(',')
        for piece in pieces:
            times = [time_piece.strip() for time_piece in piece.split('-')]
            if len(times) == 2:
                times = self._get_times(times[0], times[1])
            elif len(times) == 1:
                current_time = self._get_time(time.strptime(
                    times[0], '%H:%M'))
                times = [TimeTuple(hour=current_time.hour,
                                   minute=current_time.minute)]

            for time_object in times:
                result.add(time_object)
        return result

    def _get_times(self, start_time_s: str, end_time_s: str):
        """
        Returns a list of created Time objects with values
        in between `start_time_s` and `end_time_s`
        """
        # TODO shitty?? yes shitty
        result = []

        end_time = self._get_time(time.strptime(
            end_time_s, '%H:%M'))

        current_time = self._get_time(time.strptime(
            start_time_s, '%H:%M'))

        while current_time != end_time:
            result.append(TimeTuple(hour=current_time.hour,
                                    minute=current_time.minute))
            current_time += datetime.timedelta(minutes=TimeSlot.DURATION)
        return result

    def _get_time(self, time):
        time = datetime.time(hour=time.tm_hour, minute=time.tm_min)
        return datetime.datetime.combine(timezone.now().date(), time)

    class Meta:
        model = Schedule
        fields = ('time_slots', 'date')
