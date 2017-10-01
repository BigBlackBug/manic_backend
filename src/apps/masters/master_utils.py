import heapq
from typing import Iterator

from src.apps.masters.models import Master


class MasterComparable:
    def __init__(self, master, value):
        self.master = master
        self.value = value

    def __lt__(self, other):
        return self.value < other.value


def sort_masters(masters: Iterator[Master], coordinates: tuple, max_distance: float):
    """
    returns tuple (favorites, others)
    :param max_distance:
    :param masters:
    :param coordinates:
    :return:
    """
    assert coordinates
    result = []
    # 1-(master.distance(*coordinates)/max_distance) * 3 [1 - рядом]
    # 1-(master.rating/max_rating) * 7 [1 - суперстар]
    # distance and rating
    for master in masters:
        distance = master.distance(*coordinates) if coordinates else 0
        value = (1 - (distance / max_distance)) * 3 + (1 - (master.rating / Master.MAX_RATING) * 7)
        heapq.heappush(result, MasterComparable(master, value))
    return [comp.master for comp in result]
