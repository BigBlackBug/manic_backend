# -*- coding: utf-8 -*-
import datetime

from django.conf import settings
from django.db import models

from src.apps.authentication.models import UserProfile
from src.apps.core.models import Location
from src.apps.core.utils import Folders


class Master(UserProfile):
    MAX_RATING = 5.0

    location = models.OneToOneField(Location, on_delete=models.CASCADE, related_name='+')

    services = models.ManyToManyField(settings.SERVICE_MODEL, related_name='masters')

    rating = models.FloatField(default=0.0)

    # FK fields
    # schedule - list of 'created schedules'
    # portfolio - list of 'portfolio images'
    # order_items - list of 'order items'

    def distance(self, lat, lon):
        return self.location.distance(lat, lon)

    def get_schedule(self, date):
        """
        Gets the schedule at `date`
        :param date:
        :return: schedule
        """
        return self.schedule.get(date=date)

    def __str__(self):
        return self.first_name

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

    @property
    def value(self):
        return self.time.value

    def __str__(self):
        return f'{self.time} - taken: {self.taken}'


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

    def __str__(self):
        return f'schedule for date {self.date}'

    def assign_time(self, time: datetime.time, number_of_slots: int):
        """
        Sets the `number_of_slots` number of time slots
        to 'taken' starting at 'time'

        :param time:
        :param number_of_slots:
        :return: time <datetime> of the next available time slot or None if
        the last processed slot marks the end of the work day
        """
        if not time:
            raise ValueError('time argument should not be None')

        time_slots = sorted(self.time_slots.all(), key=lambda slot: slot.value)

        # looking for the first timeslot
        for first_slot_index, time_slot in enumerate(time_slots):
            if time_slot.value == time:
                break
        else:
            raise ValueError('time not found')

        # TODO index error
        # TODO this method blows, potential performance issues
        shift = 0
        for shift in range(number_of_slots):
            ts = self.time_slots.get(pk=time_slots[first_slot_index + shift].id)
            ts.taken = True
            ts.save()

        next_index = first_slot_index + shift + 1
        if next_index == len(time_slots):
            return None

        return time_slots[next_index].value

# TODO referrals
# TODO feedbacks
# TODO payments
