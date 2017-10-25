import datetime
from typing import Iterator

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

    # the last block may ignore +1 slot, because there can't be subsequent orders
    if block_size >= slot_number - 1:
        indices.append(start_index)
    return [time_slots[index] for index in indices]


def service_fits_into_slots(service: Service, time_slots: Iterator[TimeSlot],
                            time_from: datetime.time, time_to: datetime.time):
    """
    Returns true if `service` can be done in the given list of slots
    i.e. `time_slots` contains at least one sequence of available slots which is
    `service.max_duration + TimeSlot.DURATION` minutes long within the given time frame

    *NOTE* slot at `time_to` is excluded

    :param service:
    :param time_slots:
    :param time_from:
    :param time_to:
    :return:
    """
    time_slots = list(
        filter(lambda slot: time_from <= slot.value < time_to, time_slots))
    return len(find_available_starting_slots(service, time_slots)) != 0
