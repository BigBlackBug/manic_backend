import uuid
from math import acos, cos, radians, sin

from django.db import models


class UUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Location(models.Model):
    lat = models.FloatField()
    lon = models.FloatField()

    def distance(self, lat, lon):
        # Great circle distance formula
        return 6371 * acos(
            cos(radians(lat)) * cos(radians(self.lat)) *
            cos(radians(self.lon) - radians(lon)) +
            sin(radians(lat)) * sin(radians(self.lat))
        )

    def as_tuple(self):
        return self.lat, self.lon

    def __str__(self):
        return "lat:{}, lon:{}".format(self.lat, self.lon)
