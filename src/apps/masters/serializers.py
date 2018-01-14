import datetime
import logging

from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from src.apps.categories.models import Service
from src.apps.categories.serializers import ServiceSerializer
from src.apps.clients.serializers import SimpleClientSerializer
from src.apps.core.exceptions import ApplicationError
from src.apps.core.mixins import FilterEmptyFieldsMixin
from src.apps.core.models import Location
from src.apps.core.serializers import LocationSerializer
from src.apps.masters import time_slot_utils
from .models import Master, Schedule, TimeSlot, Time, MasterStatus, Feedback, \
    Balance

logger = logging.getLogger(__name__)


class TimeSlotSerializer(serializers.ModelSerializer):
    time = serializers.SerializerMethodField()
    order_id = serializers.SerializerMethodField()

    def get_order_id(self, time_slot):
        return time_slot.order_item and \
               time_slot.order_item.order and \
               time_slot.order_item.order.id

    def get_time(self, time_slot: TimeSlot):
        # chopping off seconds
        return str(time_slot.time.value)[:-3]

    class Meta:
        model = TimeSlot
        fields = ('time', 'taken', 'order_id')


class ScheduleSerializer(serializers.ModelSerializer):
    time_slots = TimeSlotSerializer(many=True, read_only=True)

    class Meta:
        model = Schedule
        exclude = ('id', 'master')


class CreateFeedbackSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(max_value=5, min_value=0)
    text = serializers.CharField(max_length=1024)

    def create(self, validated_data):
        client = self.context['request'].user.client
        master = self.context['master']
        feedback = Feedback.objects.create(client=client,
                                           master=master,
                                           **validated_data)
        master.add_rating(feedback.rating)
        logger.info(f'Adding {feedback.rating} star feedback '
                    f'to master {master.first_name}')
        master.save()
        return feedback

    class Meta:
        model = Feedback
        fields = ('rating', 'text', 'date')


class FeedbackSerializer(serializers.ModelSerializer):
    client = SimpleClientSerializer(read_only=True)

    class Meta:
        model = Feedback
        fields = ('rating', 'text', 'date', 'client')


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Balance
        exclude = ('id', 'master')


class PortfolioSerializer(serializers.Serializer):
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


class MasterSerializer(serializers.ModelSerializer):
    """
    Provides a complete representation of a master
    """

    location = LocationSerializer(read_only=True)
    services = ServiceSerializer(many=True, read_only=True)
    schedule = serializers.SerializerMethodField(read_only=True)
    portfolio = serializers.SerializerMethodField(read_only=True)
    feedback = FeedbackSerializer(many=True, read_only=True)
    balance = BalanceSerializer(read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)

    def get_portfolio(self, master: Master):
        portfolio = master.portfolio.order_by('-added').all()
        serializer = PortfolioSerializer(many=True,
                                         instance=portfolio,
                                         context=self.context)
        return serializer.data

    def get_schedule(self, master: Master):
        """
        Only schedules for upcoming dates are returned
        """
        schedules = master.schedule.filter(date__gte=timezone.now()) \
            .order_by('date').all()
        serializer = ScheduleSerializer(many=True, instance=schedules)
        return serializer.data

    class Meta:
        model = Master
        exclude = ('user',)


class SimpleMasterSerializer(FilterEmptyFieldsMixin,
                             serializers.ModelSerializer):
    """
    Provides a short representation of a master, to be used in the
    main list of masters.

    Ignores `available_slots` field if it's empty
    """
    DISTANCE_NOT_AVAILABLE = -1

    services = ServiceSerializer(many=True, read_only=True)
    location = LocationSerializer(read_only=True)
    distance = serializers.SerializerMethodField('_distance', read_only=True)

    # may be omitted
    available_slots = serializers.SerializerMethodField('_available_slots',
                                                        read_only=True)
    avatar = serializers.ImageField()

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
        logging.info(f'Creating schedule on {schedule.date} '
                     f'for master {master.first_name}. '
                     f'time_slots={time_tuples}')
        for time_tuple in time_tuples:
            try:
                target_time = datetime.time(hour=time_tuple.hour,
                                            minute=time_tuple.minute)
                TimeSlot.objects.get(schedule=schedule,
                                     time__value=target_time)
            except TimeSlot.DoesNotExist:
                TimeSlot.objects.create(
                    time=Time.objects.create(hour=time_tuple.hour,
                                             minute=time_tuple.minute),
                    schedule=schedule,
                    taken=False)
            else:
                raise ApplicationError(f'Trying to overwrite time slot'
                                       f' at {target_time}')
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


class IdListField(serializers.Field):
    def to_internal_value(self, data):
        if isinstance(data, str):
            if len(data) == 0:
                raise ValidationError('Empty Id List field')
            return [service.strip() for service in data.split(',')]
        else:
            raise ValidationError('Wrong field type')


class MasterCreateSerializer(serializers.ModelSerializer):
    services = IdListField(write_only=True, required=True)
    avatar = serializers.ImageField(write_only=True, required=True)

    def create(self, validated_data):
        services = validated_data.pop('services', [])
        master = self.context['request'].user.master
        master.status = MasterStatus.ON_REVIEW
        for (key, value) in validated_data.items():
            setattr(master, key, value)

        for service in services:
            master.services.add(Service.objects.get(pk=service))
        logger.info(f'Creating master. ID={master.id}, '
                    f'first_name={master.first_name}, '
                    f'status={master.status}')
        master.save()
        # initializing balance
        logger.info(f'Initializing masters {master.first_name} balance')
        Balance.objects.create(master=master)
        return master

    class Meta:
        model = Master
        fields = ('id', 'first_name', 'gender', 'avatar', 'date_of_birth',
                  'email', 'about', 'services', 'location')


class MasterUpdateSerializer(serializers.ModelSerializer):
    services = IdListField(write_only=True)
    location = LocationSerializer(write_only=True)

    def get_fields(self):
        fields = super().get_fields()
        for field in fields.values():
            field.required = False
        return fields

    def update(self, instance, validated_data):
        new_services = validated_data.pop('services', [])
        new_location = validated_data.pop('location', None)
        if new_services:
            logger.info(f'Updating masters {instance.first_name} services. '
                        f'New services={new_services}')
            instance.services = [Service.objects.get(pk=service) for service in
                                 new_services]
        if new_location:
            logger.info(f'Updating masters location {new_location}')
            serializer = LocationSerializer(data=new_location)
            serializer.is_valid(raise_exception=True)

            instance.location = Location.objects.create(
                **serializer.validated_data)
        return super().update(instance, validated_data)

    class Meta:
        model = Master
        fields = ('id', 'first_name', 'gender', 'date_of_birth',
                  'email', 'about', 'services', 'location', 'status')
