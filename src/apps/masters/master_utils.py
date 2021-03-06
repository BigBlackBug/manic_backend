import heapq
import logging
from typing import Iterable

from src.apps.clients.models import Client
from src.apps.masters import time_slot_utils
from src.apps.masters.filtering import FilteringParams
from src.apps.masters.models import Master, MasterStatus
from src.apps.masters.serializers import SimpleMasterSerializer

logger = logging.getLogger(__name__)


class MasterComparable:
    def __init__(self, master, value):
        self.master = master
        self.value = value

    def __lt__(self, other):
        # max sort
        return other.value < self.value


def _evaluate_master(distance, max_distance, rating,
                     max_rating=Master.MAX_RATING):
    return (1 - (distance / max_distance)) * 3 + (rating / max_rating) * 7


def sort_masters(masters: Iterable[Master], coordinates: tuple,
                 max_distance: float):
    """
    Sorts `masters` according to rating and distance to `coordinates`
    Rating is responsible for 70% of the total value,
    and distance is for the other 30%
    :param max_distance:
    :param masters:
    :param coordinates:
    :return:
    """
    result = []
    for master in masters:
        distance = master.distance(*coordinates) if coordinates else 0
        value = _evaluate_master(distance=distance,
                                 max_distance=max_distance,
                                 rating=master.rating)
        heapq.heappush(result, MasterComparable(master, value))
    return [comp.master for comp in result]


def search(params: FilteringParams, filter_function):
    # TODO docs
    date_range = params.date_range
    services = params.services
    coordinates = params.coordinates
    max_distance = params.distance

    logger.info(f'Initiating master search with params: '
                f'date_range={date_range}, services={services}, '
                f'coordinates={coordinates}, max_distance={max_distance}')
    # queryset
    queryset = Master.objects.filter(schedule__date__gte=date_range[0],
                                     schedule__date__lte=date_range[1],
                                     services__in=services,
                                     status=MasterStatus.VERIFIED).distinct() \
        .prefetch_related('services').prefetch_related('schedule__time_slots') \
        .select_related('location')

    # search filter
    masters, slots = filter_function(queryset, params)

    logger.info(f'Found {len(masters)} masters. Running distance filter')
    # distance filter
    masters = list(filter(lambda m: m.distance(*coordinates) < max_distance,
                          masters))
    logger.info(f'Total masters found: {len(masters)}')
    return masters, slots


def upsale_search(order_items, order_date):
    """
    Returns masters and services that they can do on `order_date`
    with respect to the `order_items`

    :param order_items:
    :param order_date:
    :return:
    """
    logger.info(f'Using an upsale search filter on items {order_items} '
                f'with params: date={order_date}')

    # taking the maximum duration of all services of the master and
    # checking if there exists a required number of adjacent empty slots
    result = []
    for item in order_items:
        master = Master.objects.get(pk=item['master_id'])

        logger.info(f'Checking master {master.first_name}')
        schedule = master.get_schedule(order_date)
        logger.info(f'Checking schedule on {schedule.date}')

        for service in master.services.exclude(pk__in=item['service_ids']):
            # ignoring certain services
            time = item['time']
            if time_slot_utils.service_fits_into_slots(
                    service, schedule.time_slots.all(),
                    time_from=time):
                logger.info(f'Master can do service {service.name} '
                            f'on {schedule.date} at {time}')
                result.append({
                    'master_id': master.id,
                    'service_id': service.id
                })
    return result


def split(masters, target_client: Client):
    """
    splits `masters` into two lists - favorites, who have served
    `target_client` at least once and those who haven't
    :param masters:
    :param target_client:
    :return: <tuple> favorites, regular
    """
    regular = []
    favorites = []

    logger.info(f'Splitting {len(masters)} masters')

    for master in masters:
        # TODO cache
        if target_client and master.times_served(target_client) > 0:
            favorites.append(master)
        else:
            regular.append(master)

    logger.info(f'Favorites {len(favorites)}, regular {len(regular)}')
    return favorites, regular


def sort_and_serialize_masters(request, masters: Iterable[Master],
                               params: FilteringParams,
                               slots: dict):
    """
    Runs `master_utils.sort_master` and then serializes the list
    :param masters:
    :param params:
    :param slots: a dict, which contains
    :return:
    """
    masters = sort_masters(masters, params.coordinates, params.distance)
    # TODO JUNK!!!
    logging.info(f'Serializing sorted master list len={len(masters)}')
    serializer = SimpleMasterSerializer(masters, many=True, context={
        'request': request,
        'coordinates': params.coordinates,
        'available_slots': slots
    })
    return serializer.data
