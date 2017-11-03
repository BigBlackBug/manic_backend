import datetime
import logging
from collections import defaultdict
from enum import Enum
from time import strptime
from typing import Iterable

from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from src.apps.categories.models import Service
from . import time_slot_utils, gmaps_utils, utils
from .models import Master

MAX_DISTANCE_KM = 2000.0

available_params = ['date_between', 'time_between', 'services',
                    'service', 'coordinates', 'distance', 'date',
                    'time']

logger = logging.getLogger(__name__)


class FilteringParams:
    def __init__(self, request: Request, coords_required=True):
        query_params = request.query_params
        logger.info(f'Parsing {query_params}')

        self._validate(query_params)
        self.services = self._parse_services(query_params)
        self.service = self._parse_service(query_params)
        self.date_range = self._parse_date(query_params)
        self.date = self._parse_single_date(query_params)
        self.time = self._parse_single_time(query_params)
        self.time_range = self._parse_time(query_params)
        if coords_required:
            self.coordinates = self._parse_coordinates(query_params)
        self.distance = self._parse_distance(query_params)
        self.target_client = self._parse_client(request)

    @staticmethod
    def _parse_service(query_params):
        service = query_params.get('service')
        if not service:
            return None
        try:
            service = int(service)
        except ValueError:
            raise ValidationError("'service' parameters must be an integer")
        else:
            return service

    @staticmethod
    def _validate(query_params):
        unrecognized_params = []
        for param in query_params:
            if param not in available_params:
                unrecognized_params.append(param)

        if unrecognized_params:
            raise ValidationError(
                f'unrecognized parameters {unrecognized_params}')

    @staticmethod
    def _parse_services(query_params):
        service = FilteringParams._parse_service(query_params)
        if service:
            return [service]

        services = query_params.get('services')
        if not services:
            # TODO cache
            return [service.id for service in Service.objects.all()]
        else:
            services = services.split(',')
            for service_id in services:
                try:
                    int(service_id)
                except ValueError:
                    raise ValidationError('invalid service string')
            return services

    @staticmethod
    def _parse_date(query_params):
        # TODO validate that it's a list
        date_range = query_params.get('date_between')
        if date_range:
            dates = date_range.split(',')
            if len(dates) != 2:
                raise ValidationError('invalid date range')
            try:
                dates = (
                    datetime.datetime.strptime(dates[0], '%Y-%m-%d'),
                    datetime.datetime.strptime(dates[1], '%Y-%m-%d'))
            except ValueError:
                raise ValidationError('invalid date format')
        else:
            dates = utils.get_default_date_range()
        return dates

    @staticmethod
    def _parse_time(query_params):
        time_range = query_params.get('time_between')
        if time_range:
            times = time_range.split(',')
            if len(times) != 2:
                raise ValidationError('invalid time range')

            try:
                time_0 = strptime(times[0], '%H:%M')
                time_1 = strptime(times[1], '%H:%M')
                times = (
                    datetime.time(hour=time_0.tm_hour, minute=time_0.tm_min),
                    datetime.time(hour=time_1.tm_hour, minute=time_1.tm_min))
            except ValueError:
                raise ValidationError('invalid time format')
        else:
            times = (datetime.time(hour=8, minute=0),
                     datetime.time(hour=22, minute=30))
        return times

    @staticmethod
    def _parse_coordinates(query_params):
        # these could be either client's current coordinates
        # or address coords (don't pay attention, it's an app's job)
        coordinates = query_params.get('coordinates')
        if not coordinates:
            raise ValidationError("please send coordinates")

        coordinates = coordinates.split(',')
        if len(coordinates) != 2:
            raise ValidationError('invalid coordinates range')
        try:
            return float(coordinates[0]), float(coordinates[1])
        except ValueError:
            raise ValidationError('invalid coordinates format')

    @staticmethod
    def _parse_distance(query_params):
        # считаем расстояние до адреса
        distance = query_params.get('distance')
        if not distance:
            return MAX_DISTANCE_KM
        else:
            return float(distance)

    @staticmethod
    def _parse_client(request):
        if not request.user.is_client():
            # TODO proper exception
            raise ValueError('not a client')

        return request.user.client

    @staticmethod
    def _parse_single_date(query_params):
        date = query_params.get('date')
        if date:
            try:
                date = datetime.datetime.strptime(date, '%Y-%m-%d')
                date_range = utils.get_default_date_range()
                if date < date_range[0] or date > date_range[1]:
                    raise ValidationError(
                        'date must be withing two weeks range')
                return date
            except ValueError:
                raise ValidationError('invalid date format')
        else:
            return None

    @staticmethod
    def _parse_single_time(query_params):
        time = query_params.get('time')
        if time:
            try:
                time = time.strptime(time, '%H:%M')
                return datetime.time(hour=time.tm_hour, minute=time.tm_min)
            except ValueError:
                raise ValidationError('invalid time format')
        else:
            return None


class FilteringFunctions(Enum):
    @staticmethod
    def datetime(masters: Iterable[Master], params: FilteringParams):
        """
        Returns a list of masters who can do the specific service
        at specific date and time for the specific client, taking into account
        the possibility to get to the client

        :param masters: masters to filter
        :param params:
        :return:
        """
        service_id = params.service
        date = params.date
        time = params.time
        target_client = params.target_client

        result = set()
        good_slots = defaultdict(list)
        for master in masters:
            service = master.services.get(pk=service_id)
            schedule = master.get_schedule(date)
            can_service = time_slot_utils \
                .service_fits_into_slots(service, schedule.time_slots.all(),
                                         time, time)
            # checking the closest order that goes before `time`
            if can_service and gmaps_utils.can_reach(
                    schedule, target_client.home_address.location, time):
                result.add(master)
            good_slots[master.id].append({
                'date': schedule.date.strftime('%Y-%m-%d'),
                'time_slots': [datetime.time.strftime(time, '%H:%M')]
            })
        return result, good_slots

    @staticmethod
    def anytime(masters: Iterable[Master], params: FilteringParams):
        """
        Returns a list of masters who can do the specific service
        at any time in the `date_range` for the specific client,
        taking into account the possibility to get to the client

        :param masters: masters to filter
        :param params:
        :return:
        """
        date_range = params.date_range
        service_id = params.service
        target_client = params.target_client

        result = set()
        good_slots = defaultdict(list)
        for master in masters:
            service = master.services.get(pk=service_id)
            for schedule in master.schedule.filter(date__gte=date_range[0],
                                                   date__lte=date_range[1]):
                schedule_slots = []
                # finding all slots that can be used to do the service
                start_slots = time_slot_utils.find_available_starting_slots(
                    service, schedule.time_slots.all())
                for slot in start_slots:
                    # checking if the master can get to the next address in time
                    if gmaps_utils.can_reach(schedule,
                                             target_client.home_address.location,
                                             slot.value):
                        result.add(master)
                        schedule_slots.append(
                            datetime.time.strftime(slot.value, '%H:%M'))

                if schedule_slots:
                    good_slots[master.id].append({
                        'date': schedule.date.strftime('%Y-%m-%d'),
                        'time_slots': schedule_slots
                    })

        return result, good_slots

    @staticmethod
    def search(masters: Iterable[Master], params: FilteringParams):
        """
        Returns a list of masters who can do any of his services
        at any time in `time_range` and date in the `date_range`
        for the specific client, taking into account the possibility
        to get to the client

        :param masters: masters to filter
        :param params:
        :return:
        """
        date_range = params.date_range
        time_range = params.time_range
        # taking the maximum duration of all services of the master and
        # checking if there exists a required number of adjacent empty slots
        result = set()
        for master in masters:
            # checking if a master can do any service during his work day
            service = min(master.services.all(), key=lambda _: _.max_duration)
            for schedule in master.schedule.filter(date__gte=date_range[0],
                                                   date__lte=date_range[1]):
                if time_slot_utils.service_fits_into_slots(
                        service, schedule.time_slots.all(),
                        time_range[0], time_range[1]):
                    result.add(master)
        return result, {}
