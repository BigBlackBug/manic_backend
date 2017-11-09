from unittest import skip
from unittest.mock import MagicMock, PropertyMock

from rest_framework.test import APITestCase

from src.apps.masters import master_utils


def make_generic_mock(**kwargs):
    mock = MagicMock()
    for k, v in kwargs.items():
        prop = PropertyMock(return_value=v)
        setattr(type(mock), k, prop)
    return mock


def make_master_mock(id=None, distance=None, rating=None, times_served=None):
    mock = MagicMock()
    if distance is not None:
        mock.distance.return_value = distance
    if rating is not None:
        rating_prop = PropertyMock(return_value=rating)
        type(mock).rating = rating_prop

    if id is not None:
        id_prop = PropertyMock(return_value=id)
        type(mock).id = id_prop

    if times_served is not None:
        mock.times_served.return_value = times_served

    return mock


class SortTestCase(APITestCase):
    def test_sort(self):
        masters = [make_master_mock(id=0, distance=10, rating=3),
                   make_master_mock(id=1, distance=4, rating=5),
                   make_master_mock(id=2, distance=5, rating=3),
                   make_master_mock(id=3, distance=1, rating=0.4)]
        result = master_utils.sort_masters(masters, coordinates=(10, 10),
                                           max_distance=10)
        for master in masters:
            master.distance.assert_called_once()
        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[1].id, 0)
        self.assertEqual(result[2].id, 2)
        self.assertEqual(result[3].id, 3)


class SearchFilteringTestCase(APITestCase):
    # TODO test
    pass


class DateTimeFilteringTestCase(APITestCase):
    # TODO test
    pass


class AnytimeFilteringTestCase(APITestCase):
    # TODO test
    pass


# TODO rewrite and unskip
class SplitTestCase(APITestCase):
    @skip
    def test_split(self):
        masters = [
            make_master_mock(id=0, times_served=1),
            make_master_mock(id=1, times_served=2),
            make_master_mock(id=2, times_served=0),
            make_master_mock(id=3, times_served=12)
        ]
        favs, regular = master_utils.split(masters, target_client=None)
        self.assertEqual(len(regular), 3)
        self.assertIn(masters[0], regular)
        self.assertIn(masters[1], regular)
        self.assertIn(masters[3], regular)
        self.assertEqual(len(regular), 1)
        self.assertIn(masters[2], regular)

    @skip
    def test_split_no_favs(self):
        masters = [
            make_master_mock(id=0, times_served=0),
            make_master_mock(id=1, times_served=0),
            make_master_mock(id=2, times_served=0),
        ]
        favs, regular = master_utils.split(masters, target_client=None)
        self.assertEqual(len(favs), 0)

        self.assertEqual(len(regular), 3)
        self.assertIn(masters[0], regular)
        self.assertIn(masters[1], regular)
        self.assertIn(masters[2], regular)

    @skip
    def test_split_no_regular(self):
        masters = [
            make_master_mock(id=0, times_served=1),
            make_master_mock(id=1, times_served=2),
            make_master_mock(id=2, times_served=5),
            make_master_mock(id=3, times_served=12)
        ]
        favs, regular = master_utils.split(masters, target_client=None)
        self.assertEqual(len(favs), 4)
        self.assertIn(masters[0], favs)
        self.assertIn(masters[1], favs)
        self.assertIn(masters[2], favs)
        self.assertIn(masters[3], favs)
        self.assertEqual(len(regular), 0)

    @skip
    def test_split_empty(self):
        masters = []
        favs, regular = master_utils.split(masters, target_client=None)
        self.assertEqual(len(favs), 0)
        self.assertEqual(len(regular), 0)
