import datetime
import time
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from src.apps.categories.models import Service
from src.apps.masters import time_slot_utils
from .models import Master

MAX_DISTANCE_KM = 2000.0

available_params = ['date_between', 'time_between', 'services', 'coordinates', 'distance']


def prepare_filtering_params(query_params: dict):
    unrecognized_params = []
    for param in query_params:
        if param not in available_params:
            unrecognized_params.append(param)

    if unrecognized_params:
        raise ValidationError(f'unrecognized parameters {unrecognized_params}')

    result = {}
    services = query_params.get('services')
    if not services:
        # TODO cache
        result['services'] = [service.id for service in Service.objects.all()]
    else:
        services = services.split(',')
        for service_id in services:
            try:
                int(service_id)
            except ValueError:
                raise ValidationError('invalid service string')
        result['services'] = services

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
        now = timezone.now()
        dates = (now.date(), now.date() + datetime.timedelta(days=14))
    result['date_range'] = dates

    time_range = query_params.get('time_between')
    if time_range:
        times = time_range.split(',')
        if len(times) != 2:
            raise ValidationError('invalid time range')

        try:
            time_0=time.strptime(times[0], '%H:%M')
            time_1 = time.strptime(times[1], '%H:%M')
            times = (
                datetime.time(hour=time_0.tm_hour,minute=time_0.tm_min),
                datetime.time(hour=time_1.tm_hour, minute=time_1.tm_min))
        except ValueError:
            raise ValidationError('invalid time format')
    else:
        times = (datetime.time(hour=8, minute=0), datetime.time(hour=22, minute=30))
    result['time_range'] = times

    # these could be either client's current coordinates
    # or address coords (don't pay attention, it's an app's job)
    coordinates = query_params.get('coordinates')
    if not coordinates:
        raise ValidationError("please send coordinates")

    coordinates = coordinates.split(',')
    if len(coordinates) != 2:
        raise ValidationError('invalid coordinates range')
    try:
        result['coordinates'] = (float(coordinates[0]), float(coordinates[1]))
    except ValueError:
        raise ValidationError('invalid coords format')

    # считаем расстояние до адреса
    distance = query_params.get('distance')
    if not distance:
        result['distance'] = MAX_DISTANCE_KM
    else:
        result['distance'] = float(distance)
    return result


def search_for_masters(filtering_params):
    """
    ДЛЯ ПОИСКА ВО ВКЛАДКЕ МАСТЕРА
    :param filtering_params:
    :return:
    """
    date_range = filtering_params['date_range']
    time_range = filtering_params['time_range']
    services = filtering_params['services']
    coordinates = filtering_params['coordinates']
    max_distance = filtering_params['distance']

    # а вот теперь фильтруем.
    # сначала по сервисам - все мастера, которые хотя б одну услугу оказывают
    # работают хотя б в один день
    queryset = Master.objects.filter(schedule__date__gte=date_range[0],
                                     schedule__date__lte=date_range[1],
                                     services__in=services, ).distinct() \
        .prefetch_related('services').prefetch_related('schedule__time_slots') \
        .select_related('location')
    # а теперь смотрим, может ли он на самом деле это сделать судя по таймслотам
    # то есть берем макс длительность сервиса и ищем такое вхождение в таймслотах шедуля
    # то есть вася может сделать маникюр и работает во вторник, а петя в среду педикюр
    result = set()
    for master in queryset:
        # хоть какую-нить услугу он успеет сделать во рабочее время
        service = min(master.services.all(),
                      key=lambda service_: service_.max_duration)
        for schedule in master.schedule.all():
            if time_slot_utils.service_fits_into_slots(service, schedule.time_slots.all(),
                                                       time_range[0], time_range[1]):
                result.add(master)

    # готовых пацанов уже в питоне фильтруем по расстоянию
    return filter(lambda m: m.distance(*coordinates) < max_distance, result)
