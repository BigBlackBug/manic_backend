import datetime
import logging
import time
from collections import defaultdict
from enum import Enum
from time import strptime
from typing import Iterable

from django.conf import settings
from rest_framework.exceptions import ValidationError

from src.apps.categories.models import Service
from src.apps.masters.time_slot_utils import add_time
from . import time_slot_utils, gmaps_utils, utils
from .models import Master

available_params = ['date_range', 'time_range', 'services',
                    'service', 'coordinates', 'distance', 'date',
                    'time']

logger = logging.getLogger(__name__)


class FilteringParams:
    def __init__(self, query_params: dict, client=None, request=None,
                 coords_required=True, ignore_taken_slots=False):
        logger.info(f'Parsing {query_params}')

        self._validate(query_params)
        self.services = self._parse_services(query_params)
        self.service = self._parse_service(query_params)
        self.date_range = self._parse_date(query_params)
        self.date = self._parse_single_date(query_params)
        self.time = self._parse_single_time(query_params)
        self.time_range = self._parse_time(query_params)
        self.ignore_taken_slots = ignore_taken_slots
        if coords_required:
            self.coordinates = self._parse_coordinates(query_params)
        self.distance = self._parse_distance(query_params)

        if client:
            self.target_client = client
        elif request:
            self.target_client = self._parse_client(request)

    @staticmethod
    def _parse_service(query_params):
        service = query_params.get('service')
        if not service:
            return None
        try:
            logger.debug(f'Parsed service {service}')
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
                f'Unrecognized parameters {unrecognized_params}')

    @staticmethod
    def _parse_services(query_params):
        service = FilteringParams._parse_service(query_params)
        if service:
            return [service]

        services = query_params.get('services')
        if not services:
            # TODO cache
            logger.debug(f'No services param, returning all services')
            return [service.id for service in Service.objects.all()]
        else:
            services = services.split(',')
            for service_id in services:
                try:
                    int(service_id)
                except ValueError:
                    raise ValidationError('Invalid service string')
            logger.debug(f'Parsed services {services}')
            return services

    @staticmethod
    def _parse_date(query_params):
        # TODO validate that it's a list
        date_range = query_params.get('date_range')
        if date_range:
            dates = date_range.split(',')
            if len(dates) != 2:
                raise ValidationError('Invalid date range')
            try:
                dates = (
                    datetime.datetime.strptime(dates[0], '%Y-%m-%d'),
                    datetime.datetime.strptime(dates[1], '%Y-%m-%d'))
                logger.debug(f'Parsed date_range {dates}')
            except ValueError:
                raise ValidationError('Invalid date format')
        else:
            logger.debug(f'No date_range param, using default (2 weeks)')
            dates = utils.get_default_date_range()
        return dates

    @staticmethod
    def _parse_time(query_params):
        time_range = query_params.get('time_range')
        if time_range:
            times = time_range.split(',')
            if len(times) != 2:
                raise ValidationError('Invalid time range')

            try:
                time_0 = strptime(times[0], '%H:%M')
                time_1 = strptime(times[1], '%H:%M')
                times = (
                    datetime.time(hour=time_0.tm_hour, minute=time_0.tm_min),
                    datetime.time(hour=time_1.tm_hour, minute=time_1.tm_min))
                logger.debug(f'Parsed time_range {times}')
            except ValueError:
                raise ValidationError('Invalid time format')
        else:
            times = (datetime.time(hour=8, minute=0),
                     datetime.time(hour=22, minute=30))
            logger.debug(f'No time_range param, using default (8:00-22:30)')
        return times

    @staticmethod
    def _parse_coordinates(query_params):
        # these could be either client's current coordinates
        # or address coords (don't pay attention, it's an app's job)
        coordinates = query_params.get('coordinates')
        if not coordinates:
            raise ValidationError("Please send coordinates")

        coordinates = coordinates.split(',')
        if len(coordinates) != 2:
            raise ValidationError('Invalid coordinates range')
        try:
            coords = float(coordinates[0]), float(coordinates[1])
            logger.debug(f'Parsed coordinates {coords}')
            return coords
        except ValueError:
            raise ValidationError('Invalid coordinates format')

    @staticmethod
    def _parse_distance(query_params):
        # считаем расстояние до адреса
        distance = query_params.get('distance')
        if not distance:
            logger.debug(f'No distance param, using default '
                         f'{settings.MAX_DISTANCE_KM}')
            return settings.MAX_DISTANCE_KM
        else:
            logger.debug(f'Parsed distance {distance}')
            return float(distance)

    @staticmethod
    def _parse_client(request):
        # hail python magic
        # returns either client or None
        client = request.user.is_client(request) and request.user.client or None
        logger.debug(f'Parsed client {client and client.first_name}')
        return client

    @staticmethod
    def _parse_single_date(query_params):
        date = query_params.get('date')
        if date:
            try:
                date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
                date_range = utils.get_default_date_range()
                if date < date_range[0] or date > date_range[1]:
                    raise ValidationError(
                        'Date must be withing two weeks range')
                logger.debug(f'Parsed single date {date}')
                return date
            except ValueError:
                raise ValidationError('Invalid date format')
        else:
            logger.debug(f'No date param')
            return None

    @staticmethod
    def _parse_single_time(query_params):
        _time = query_params.get('time')
        if _time:
            try:
                _time = time.strptime(_time, '%H:%M')
                _time = datetime.time(hour=_time.tm_hour, minute=_time.tm_min)
                logger.debug(f'Parsed single time {_time}')
                return _time
            except ValueError:
                raise ValidationError('Invalid time format')
        else:
            logger.debug(f'No time param')
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
        service_ids = params.services
        date = params.date
        time = params.time
        target_client = params.target_client

        logger.info(f'Using a datetime filter on masters {masters} '
                    f'with params: services={service_ids}, date={date}, '
                    f'time={time}, client_id={target_client.id}, '
                    f'client_name={target_client.first_name}')

        result = set()
        good_slots = defaultdict(list)
        for master in masters:
            logger.info(f'Checking master {master.first_name}')

            duration = sum([service.max_duration for service in
                            master.services.filter(pk__in=service_ids)])
            schedule = master.get_schedule(date)
            if not schedule:
                continue

            can_service = time_slot_utils \
                .duration_fits_into_slots(
                    duration, schedule.time_slots.all(),
                    time_from=time,
                    time_to=add_time(time, minutes=duration),
                    ignore_taken_slots=params.ignore_taken_slots)
            logger.info(f'Master {master.first_name} can do all services'
                        f'{service_ids} on {date} = {can_service}')
            # checking the closest order that goes before `time`
            if can_service and gmaps_utils.can_reach(
                    schedule, target_client.home_address.location, time):
                logger.info(f'Selecting master {master.first_name}')
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
        service_ids = params.services
        target_client = params.target_client

        logger.info(f'Using an anytime filter on masters {masters} '
                    f'with params: services={service_ids}, '
                    f'date_range={date_range}, '
                    f'client_id={target_client.id}, '
                    f'client_name={target_client.first_name}')

        result = set()
        good_slots = defaultdict(list)
        for master in masters:
            logger.info('Checking master {master.first_name}')
            duration = sum([service.max_duration for service in
                            master.services.filter(pk__in=service_ids)])
            for schedule in master.schedule.filter(date__gte=date_range[0],
                                                   date__lte=date_range[1]):
                logger.info(f'Checking schedule on {schedule.date}')
                schedule_slots = []
                # finding all slots that can be used to do the service
                start_slots = \
                    time_slot_utils.find_available_starting_slots_for_duration(
                        duration, schedule.time_slots.all())

                logger.info(f'Possible starting slots = \"'
                            f'{[slot.time for slot in start_slots]}\"')

                for slot in start_slots:
                    # checking if the master can get to the next address in time
                    if gmaps_utils.can_reach(schedule,
                                             target_client.home_address.location,
                                             slot.value):
                        logger.info(f'Selecting slot {slot.time}')
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

        :param masters: masters to filter
        :param params:
        :return:
        """
        date_range = params.date_range
        time_range = params.time_range

        logger.info(f'Using an search filter on masters {masters} '
                    f'with params: date_range={date_range}, '
                    f'time_range={time_range}, '
                    f'and all services')

        # taking the maximum duration of all services of the master and
        # checking if there exists a required number of adjacent empty slots
        result = set()
        for master in masters:
            logger.info(f'Checking master {master.first_name}')
            # checking if a master can do any service during his work day
            service = min(master.services.all(), key=lambda _: _.max_duration)
            for schedule in master.schedule.filter(date__gte=date_range[0],
                                                   date__lte=date_range[1]):
                logger.info(f'Checking schedule on {schedule.date}')
                if time_slot_utils.service_fits_into_slots(
                        service, schedule.time_slots.all(),
                        time_from=time_range[0],
                        time_to=time_range[1]):
                    logger.info(f'Master can do one of the services '
                                f'on {schedule.date}')
                    result.add(master)
        return result, {}
