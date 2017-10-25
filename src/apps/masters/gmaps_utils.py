from datetime import datetime, timedelta

import googlemaps
from django.conf import settings
from googlemaps import exceptions as gmaps_exceptions

from src.apps.core.exceptions import ApplicationError
from src.apps.core.models import Location
from src.apps.masters.models import Schedule, TimeSlot

gmaps = googlemaps.Client(key=settings.GMAPS_API_KEY)


# TODO exception handling
def _calculate_eta(coords_from: tuple, coords_to: tuple,
                   departure_time: datetime.date):
    """
    Calculates estimated time of travel between two pairs of coordinates at specified
    `departure_time`
    :param coords_from:
    :param coords_to:
    :param departure_time:
    :return:
    """
    try:
        directions_result = gmaps.directions(coords_from,
                                             coords_to,
                                             mode="driving", language='en',
                                             departure_time=departure_time)
        result = directions_result[0]['legs'][0]['duration_in_traffic']['value']
    except gmaps_exceptions.ApiError as error:
        # TODO add detail info
        raise ApplicationError(error)
    except Exception as ex:
        raise ApplicationError(ex)
    else:
        return result


def can_reach(schedule: Schedule, location: Location, time: datetime.time):
    """

    :param schedule:
    :param location:
    :param time:
    :return: True if it's possible to reach `location` at `time` considering `schedule`
    """
    dt = datetime.combine(schedule.date, time) - \
         timedelta(minutes=TimeSlot.DURATION)
    prev_time = dt.time()
    prev_slot = schedule.get_slot(prev_time)
    if prev_slot:
        # we assume that a person can get anywhere within an hour
        if not prev_slot.taken:
            return True
        prev_address = prev_slot.order_item.order.client.address
        eta = _calculate_eta(prev_address.location.as_tuple(),
                             location.as_tuple(), dt)
        # can get to the point in 30 minutes
        return eta < TimeSlot.DURATION
    else:
        # first slot of the day?
        return True
