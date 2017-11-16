import datetime
import time
from collections import namedtuple
from typing import Iterator, List

from django.db.models import QuerySet
from django.utils import timezone

from src.apps.categories.models import Service
from .models import TimeSlot


def find_available_starting_slots(service: Service,
                                  time_slots: Iterator[TimeSlot]):
    """
    Returns a list of TimeSlots which can be the first slots for `service` to be
    served
    :param service:
    :param time_slots:
    :return:
    """
    time_slots = sorted(time_slots, key=lambda slot: slot.value)
    block_size = 0
    start_index = 0

    # +1 stands for extra slot, used to get to the next client
    slot_number = int(service.max_duration / TimeSlot.DURATION + 1)
    indices = []
    for i in range(len(time_slots)):
        slot = time_slots[i]
        if slot.taken:
            start_index = i + 1
            block_size = 0
        else:
            block_size += 1
            if slot_number == block_size:
                indices.append(start_index)
                start_index += 1
                block_size -= 1

    # the last block may ignore +1 slot
    # because there can't be subsequent orders
    if block_size >= slot_number - 1:
        indices.append(start_index)
    return [time_slots[index] for index in indices]


def add_time(source_time, **kwargs):
    """
    Adds timedelta **kwargs to the source_time and returns the
    resulting `datetime.time` value
    """
    if isinstance(source_time, datetime.datetime):
        source_time = source_time.time()
    source_time = datetime.datetime.combine(timezone.now().date(), source_time)
    return (source_time + datetime.timedelta(**kwargs)).time()


def service_fits_into_slots(service: Service, time_slots: List[TimeSlot],
                            time_from: datetime.time = None,
                            time_to: datetime.time = None):
    """
    Returns true if `service` can be done in the given list of slots
    i.e. `time_slots` contains at least one sequence of available slots which is
    `service.max_duration + TimeSlot.DURATION` minutes long within the given time frame

    *NOTE* slot at `time_to` is excluded because of common sense

    :param service:
    :param time_slots:
    :param time_from:
    :param time_to: if None, equals to the time of the last time_slot
    :return:
    """
    # just in case somebody passes the queryset
    if isinstance(time_slots, QuerySet):
        time_slots = list(time_slots)
    if len(time_slots) == 0:
        raise ValueError('time_slots list can not be empty')
    time_slots = sorted(time_slots, key=lambda slot: slot.value)

    if time_from is None:
        time_from = time_slots[0].value
    if time_to is None:
        # because we're using the exclusive comparison '<'
        time_to = add_time(time_slots[-1].value, minutes=TimeSlot.DURATION)

    if time_to > time_from:
        good_slots = list(
            filter(lambda slot: time_from <= slot.value < time_to, time_slots))
    else:
        raise ValueError('time_to argument must be '
                         'greater or equal than time_from')

    return len(find_available_starting_slots(service, good_slots)) != 0


TimeTuple = namedtuple('TimeTuple', ['hour', 'minute'])


def parse_time_slots(slots_string: str, include_last=False):
    """
    Parses a string formatted like '10:00,13:00-15:00'
    The last time_slot is not created, i.e. in this case the last
    created slot will be at 14:30.
    Duplicates are counted once

    :param include_last: whether to include the last slot in the range or not
    :param slots_string: source string
    :return: list of TimeTuple instances
    """
    # TODO maybe return time struct instead of timetuple?
    result = set()
    pieces = slots_string.split(',')
    for piece in pieces:
        times = [time_piece.strip() for time_piece in piece.strip().split('-')]
        if len(times) == 2:
            times = _get_times(times[0], times[1], include_last=include_last)
        elif len(times) == 1:
            times = _get_times(times[0], times[0], include_last=True)

        for time_object in times:
            result.add(time_object)
    return result


def _get_times(start_time_s: str, end_time_s: str, include_last=False):
    """
    Returns a list of created Time objects with values
    in between `start_time_s` and `end_time_s`
    """
    # TODO shitty?? yes shitty
    result = []

    end_time = _get_time(time.strptime(end_time_s, '%H:%M'))

    current_time = _get_time(time.strptime(start_time_s, '%H:%M'))

    while current_time != end_time:
        result.append(TimeTuple(hour=current_time.hour,
                                minute=current_time.minute))
        current_time = add_time(current_time, minutes=TimeSlot.DURATION)

    if include_last:
        result.append(TimeTuple(hour=current_time.hour,
                                minute=current_time.minute))
    return result


def _get_time(_time):
    return datetime.time(hour=_time.tm_hour, minute=_time.tm_min)
