from rest_framework import serializers

from src.apps.categories.serializers import ServiceSerializer
from src.apps.core.serializers import LocationSerializer
from .models import Master, Schedule, TimeSlot


class TimeSlotSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField('time_value')

    def time_value(self, time_slot: TimeSlot):
        # chopping off seconds
        return str(time_slot.time.value)[:-3]

    class Meta:
        model = TimeSlot
        exclude = ('id', 'schedule')


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
        return ScheduleSerializer(instance.schedule, many=True, read_only=True).data


class SimpleMasterSerializer(serializers.ModelSerializer):
    """
    Provides a short representation of a master, to be used in the
    main list of masters
    """
    DISTANCE_NOT_AVAILABLE = -1

    services = ServiceSerializer(many=True, read_only=True)
    location = LocationSerializer(read_only=True)
    distance = serializers.SerializerMethodField('_distance', read_only=True)

    available_slots = serializers.SerializerMethodField('_available_slots', read_only=True)

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
        fields = ('id', 'first_name', 'avatar', 'services',
                  'location', 'distance', 'available_slots')
