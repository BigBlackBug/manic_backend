import datetime
from typing import List

from src.apps.categories.models import Service
from .models import TimeSlot, Schedule

MAX_DISTANCE = 2000


def find_available_starting_slots(service: Service, time_slots: List[TimeSlot]):
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
    slot_number = service.max_duration / TimeSlot.DURATION
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
    if slot_number == block_size:
        indices.append(start_index)
    return [time_slots[index] for index in indices]


def fits_into_schedule(service: Service, schedule: Schedule,
                       time_from: datetime.time, time_to: datetime.time):
    """
    Returns true if `service` can be done in the given `schedule`
    i.e. `schedule.time_slots` contains at least one sequence of available slots which is
    `service.max_duration` minutes long within the given time frame
    :param service:
    :param schedule:
    :param time_from:
    :param time_to:
    :return:
    """
    max_duration = service.max_duration
    time_slots = sorted(schedule.time_slots.all(), key=lambda slot: slot.value)

    block_size = 0
    slot_number = int(max_duration / TimeSlot.DURATION)
    for slot in time_slots:
        # ignore early slots
        if slot.time.value < time_from:
            continue
        if slot.time.value > time_to:
            break
        if slot.taken:
            if slot_number <= block_size:
                return True
            else:
                block_size = 0
        else:
            block_size += 1
    if block_size >= slot_number:
        return True
    return False
