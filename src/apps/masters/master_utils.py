import heapq
from typing import Iterable

from src.apps.clients.models import Client
from src.apps.masters.filtering import FilteringParams
from src.apps.masters.models import Master
from src.apps.masters.serializers import SimpleMasterSerializer


class MasterComparable:
    def __init__(self, master, value):
        self.master = master
        self.value = value

    def __lt__(self, other):
        # max sort
        return other.value < self.value


def sort_masters(masters: Iterable[Master], coordinates: tuple, max_distance: float):
    """
    sorts `masters` according to rating and distance to `coordinates`
    :param max_distance:
    :param masters:
    :param coordinates:
    :return:
    """
    result = []
    # 1-(master.distance(*coordinates)/max_distance) * 3 [1 - рядом]
    # 1-(master.rating/max_rating) * 7 [1 - суперстар]
    # distance and rating
    for master in masters:
        distance = master.distance(*coordinates) if coordinates else 0
        value = (1 - (distance / max_distance)) * 3 + (master.rating / Master.MAX_RATING) * 7
        heapq.heappush(result, MasterComparable(master, value))
    return [comp.master for comp in result]


def search(params: FilteringParams, filter_function):
    date_range = params.date_range
    services = params.services
    coordinates = params.coordinates
    max_distance = params.distance

    # queryset
    masters = Master.objects.filter(schedule__date__gte=date_range[0],
                                    schedule__date__lte=date_range[1],
                                    services__in=services, ).distinct() \
        .prefetch_related('services').prefetch_related('schedule__time_slots') \
        .select_related('location')
    # search filter
    result = filter_function(masters, params)
    # distance filter
    return filter(lambda m: m.distance(*coordinates) < max_distance, result)


def split(masters: Iterable[Master], target_client: Client):
    """
    splits `masters` into two lists - favorites, who have served
    `target_client` at least once and those who haven't
    :param masters:
    :param target_client:
    :return: <tuple> favorites, regular
    """
    regular = []
    favorites = []
    for master in masters:
        # TODO cache
        if master.times_served(target_client) > 0:
            favorites.append(master)
        else:
            regular.append(master)

    return favorites, regular


def sort_and_serialize_masters(masters: Iterable[Master], params: FilteringParams):
    masters = sort_masters(masters, params.coordinates, params.distance)
    serializer = SimpleMasterSerializer(masters, many=True, context={
        'coordinates': params.coordinates
    })
    return serializer.data
