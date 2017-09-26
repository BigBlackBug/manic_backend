# -*- coding: utf-8 -*-
from math import acos, cos, radians, sin

from django.conf import settings
from django.db import models

from src.apps.core.utils import Folders
from .utils import Gender


class UserProfile(models.Model):
    user = models.OneToOneField(settings.USER_MODEL,
                                related_name="%(class)s",
                                related_query_name="%(class)s", )

    first_name = models.CharField(max_length=32)
    avatar = models.ImageField(upload_to=Folders.avatars)

    gender = models.CharField(
        max_length=1,
        choices=Gender.CHOICES,
        default=Gender.FEMALE,
    )

    date_of_birth = models.DateField()

    # FK fields
    # debit_cards

    def is_client(self):
        raise NotImplementedError()

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

    def __str__(self):
        return "lat:{}, lon:{}".format(self.lat, self.lon)



class Master(UserProfile):
    location = models.OneToOneField(Location, on_delete=models.CASCADE, related_name='+')

    services = models.ManyToManyField(settings.SERVICE_MODEL, related_name='masters')

    # FK fields
    # schedule - list of 'created schedules'
    # portfolio - list of 'portfolio images'

    def distance(self, lat, lon):
        return self.location.distance(lat, lon)

    def is_client(self):
        return False

    class Meta(UserProfile.Meta):
        db_table = 'master'


class PortfolioImage(models.Model):
    image = models.ImageField(upload_to=Folders.portfolio)
    master = models.ForeignKey(Master, related_name='portfolio', on_delete=models.CASCADE)


class Time(models.Model):
    """
    data is generated once on startup
    filled with 00:30
    """
    hour = models.IntegerField()
    minute = models.IntegerField()
    # populated at insertion time
    # used only for filtering
    value = models.TimeField(blank=True, null=True)

    def __str__(self):
        return '{}:{}'.format(self.hour, self.minute)


class TimeSlot(models.Model):
    DURATION = 30

    time = models.ForeignKey(Time, on_delete=models.CASCADE, related_name='+')
    taken = models.BooleanField(default=False)
    schedule = models.ForeignKey('Schedule', related_name='time_slots')


class Schedule(models.Model):
    """
    master sets his availability dates himself

    date and list of availabilities
    """
    # FK fields
    # time_slots
    master = models.ForeignKey(Master, on_delete=models.CASCADE,
                               related_name='schedule')
    date = models.DateField()

# TODO referrals
# TODO feedbacks
# TODO orders
# TODO master's portfolio
# TODO payments

# class Address(models.Model):
#     # FK fields
#     # client
#     city = models.CharField(max_length=64)
#     street_name = models.CharField(max_length=64)
#     building = models.CharField(max_length=16)
#     floor = models.IntegerField()
#     apt_number = models.IntegerField()
#     entrance = models.IntegerField()
#     has_intercom = models.BooleanField()
#
#
# class Client(UserProfile):
#     tip = models.IntegerField(default=5)
#
#     address = models.OneToOneField('Address', on_delete=models.CASCADE,
#                                    related_name='client')
#
#     def is_client(self):
#         return True
#
#     class Meta(UserProfile.Meta):
#         db_table = 'client'
