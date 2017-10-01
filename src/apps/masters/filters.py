import datetime
import heapq
from typing import List

import django_filters
from django.db.models import Count, Q, When, Case, IntegerField
from rest_framework import filters
from rest_framework.exceptions import ValidationError

from src.apps.masters.serializers import MasterListSerializer
from .models import Master, TimeSlot


# дефолтный ордеринг - расстояние(если есть координаты)+рейтинг  фейвориты сверху+

# обязательно выбрать тип сервиса так как идите нахуй
# онли сервис - показываем всех, кто оказывает хотя б один сервис со свободными слотами
# дефолт даты(+2 недели) дефолт время(00:00 - 23:30)

# сервис + дата и время - возвращаю тех мастеров, которые хотя бы в один день оказывают хотя бы одну услугу,
#  которая укладывается в их свободное время

# если выбрали только дату и время, то ставим дефолт сервисы все и ищем всех у кого есть слот
# для самой короткой услуги


def get_slot_at_time(time_slots, target_time):
    # time_slots are sorted
    # возвращаем слот с таргеттайм временем
    return slot, index


# список слотов, в котором нужно найти
def can_service_and_reach(max_duration, schedule, target_time, target_client):
    time_slots = schedule.time_slots
    # sort timeslots
    if target_time:
        slot, i = get_slot_at_time(time_slots, target_time)
        if not slot or slot.taken:
            # taken or not servicing
            return False
        if not has_free_slots(max_duration / TimeSlot.DURATION, slot):
            return False
    else:
        slot, i = get_first_okay_slot(time_slots, max_duration / TimeSlot.DURATION)

    if i == 0:
        # first order of the day
        return True

    if time_slots[i - 1] is not None:
        return can_reach(time_slots[i - 1].order.address.coords, target_client.address.coords)
    else:
        # больше чем 30 минут чтоб доехать - ok
        return True


def get_masters_who_can_service_you_at_specific_date_and_time(service_id, date, time, limit):
    """
    ДЛЯ ПОИСКА НУЖНОГО МАСТЕРА ПО ТОЧНОМУ ВРЕМЕНИ
    limit could be 1
    :return:
    """
    # выбрали сервис -> есть макс дюрейшон

    # выбрали сервис дату и время - показываем мастеров которые смогут в это время оказать услугу
    # сначала фильтруем по дате(есть ли шедуль)
    queryset = Master.objects.filter(schedule__date=date,
                                     services__id=service_id, ).distinct() \
        .prefetch_related('services').prefetch_related('schedule__time_slots').select_related(
        'location')
    # показываем мастеров, которые смогут добраться до точки за 30 минут от предыдущего заказа
    # и у которых есть нужное количество слотов(смотрим по сервису)
    result = set()
    for master in queryset:
        for service in master.services.all():
            for schedule in master.schedule.all():
                if can_service_and_reach(service.max_duration, schedule, time, target_client):
                    result.add(master)
    # TODO sort
    return result
    # если чувак не выбирает мастера, то берем топового(бест матч)


def get_masters_who_can_service_you(service_id):
    """
    ДЛЯ ПОИСКА НУЖНОГО МАСТЕРА ПРОСТО ПО СЕРВИСУ
    :return:
    """
    # выбрали сервис -> есть макс дюрейшон
    # в списке выбора мастера показываем всех мастеров отсортированных по рейтингу,
    # которые могут оказать в ближайшие 2 недели услугу хотя б в один день
    now = timezone.now()
    date_range = (now.date(), now.date() + datetime.timedelta(days=14))
    time_range = (datetime.time(hour=8, minute=0), datetime.time(hour=22, minute=30))
    queryset = Master.objects.filter(schedule__date__gte=date_range[0],
                                     schedule__date__lte=date_range[1],
                                     services__id=service_id, ).distinct() \
        .prefetch_related('services').prefetch_related('schedule__time_slots').select_related(
        'location')
    # показываем мастеров, которые смогут добраться до точки за 30 минут от предыдущего заказа
    # и у которых есть нужное количество слотов(смотрим по сервису)
    result = set()
    for master in queryset:
        for service in master.services.all():
            for schedule in master.schedule.all():
                if can_service_and_reach_any_time(service.max_duration, schedule, time_range,
                                                  target_client):
                    result.add(master)
    return result


