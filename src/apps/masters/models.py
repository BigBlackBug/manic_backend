# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models

from src.apps.core.utils import Folders
from src.apps.masters.utils import Gender


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

    def __str__(self):
        return "lat:{}, lon:{}".format(self.lat, self.lon)


class Master(UserProfile):
    coords = models.OneToOneField(Location, on_delete=models.CASCADE,
                                  related_name='+')
    services = models.ManyToManyField(settings.SERVICE_MODEL, related_name='masters')

    # FK fields
    # services
    # working_hours - list of 'availabilities'

    def is_client(self):
        return False

    class Meta(UserProfile.Meta):
        db_table = 'master'


class Time(models.Model):
    """
    data is generated once on startup
    filled with 00:30
    """
    # FK fields
    # masters
    hour = models.IntegerField()
    minute = models.IntegerField()

    def __str__(self):
        return '{}:{}'.format(self.hour, self.minute)


class Availability(models.Model):
    time = models.ForeignKey(Time, on_delete=models.CASCADE)
    working_hours = models.ForeignKey('WorkingHours', on_delete=models.CASCADE)
    taken = models.BooleanField(default=False)


class WorkingHours(models.Model):
    """
    master sets his availability dates himself
    """
    master = models.ForeignKey(Master, on_delete=models.CASCADE,
                               related_name='working_hours')
    # TODO date settings
    date = models.DateField()
    times = models.ManyToManyField(Time, through=Availability,
                                   through_fields=('working_hours', 'time'))

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
