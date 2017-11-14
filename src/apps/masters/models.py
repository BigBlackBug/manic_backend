# -*- coding: utf-8 -*-
import datetime
import time

from django.db import models

from src.apps.authentication.models import UserProfile
from src.apps.categories.models import Service
from src.apps.clients.models import Client
from src.apps.core.exceptions import ApplicationError
from src.apps.core.models import Location
from src.apps.core.utils import Folders


class MasterStatus:
    DUMMY = 'DUMMY'
    ON_REVIEW = 'ON_REVIEW'
    VERIFIED = 'VEFIRIED'

    CHOICES = (
        (DUMMY, 'Свежий мастер'),
        (ON_REVIEW, 'На модерации'),
        (VERIFIED, 'Подтверждён'),
    )


class Master(UserProfile):
    MAX_RATING = 5.0

    location = models.OneToOneField(Location, on_delete=models.CASCADE,
                                    related_name='+')

    services = models.ManyToManyField(Service, related_name='masters')

    rating = models.FloatField(default=0.0)

    about = models.TextField(max_length=512, blank=True)

    email = models.EmailField()

    status = models.CharField(max_length=9,
                              choices=MasterStatus.CHOICES,
                              default=MasterStatus.DUMMY)

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

    def times_served(self, client: Client):
        """
        Returns a number of orders that this master had with the `client`
        :param client:
        :return:
        """
        # a pinch of python functional magic
        return sum(map(lambda item: item.order.client == client,
                       self.order_items.all()))


class PortfolioOrderStatus:
    ON_MODERATION = 'ON_MODERATION'
    ACCEPTED = 'ACCEPTED'
    CHOICES = (
        (ON_MODERATION, 'На модерации'),
        (ACCEPTED, 'Принято'),
    )


class PortfolioImage(models.Model):
    image = models.ImageField(upload_to=Folders.portfolio)
    description = models.CharField(max_length=1024, blank=True)

    # status should be manually set by the administrator
    status = models.CharField(
        max_length=13,
        choices=PortfolioOrderStatus.CHOICES,
        default=PortfolioOrderStatus.ON_MODERATION,
    )
    master = models.ForeignKey(Master, related_name='portfolio',
                               on_delete=models.CASCADE)


class Time(models.Model):
    hour = models.IntegerField()
    minute = models.IntegerField()
    # populated at insertion time
    # used only for filtering
    value = models.TimeField(blank=True, null=True, editable=False)

    def __str__(self):
        minute = self.minute

        if minute == 0:
            minute = '00'
        return f'{self.hour}:{minute}'


class TimeSlot(models.Model):
    DURATION = 30
    # TODO unique schedule+time
    time = models.ForeignKey(Time, on_delete=models.CASCADE, related_name='+')
    taken = models.BooleanField(default=False)
    schedule = models.ForeignKey('Schedule', related_name='time_slots')

    order_item = models.ForeignKey('orders.OrderItem', blank=True, null=True)

    @property
    def value(self):
        return self.time.value

    def __str__(self):
        taken = 'taken' if self.taken else 'available'
        return f'{self.time} {taken}. Item ID:{self.order_item.id}'


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

    def get_slot(self, _time):
        if isinstance(_time, str):
            _time = time.strptime(_time, '%H:%M')
            _time = datetime.time(hour=_time.tm_hour, minute=_time.tm_min)

        try:
            return self.time_slots.get(time__value=_time)
        except TimeSlot.DoesNotExist:
            return None

    def delete_slot(self, time):
        """
        Deletes the time slot at specified `time` or raises ApplicationError
        if the slot is taken. Does nothing if the slot does not exist.

        :param time: str or time instance
        :return:
        """
        slot = self.get_slot(time)
        if slot:
            if not slot.taken:
                slot.delete()
            else:
                raise ApplicationError(
                    f'Slot at time {slot.time} can not be deleted '
                    f'because there is an order at that time')

    def assign_time(self, time: datetime.time, number_of_slots: int,
                    order_item=None):
        """
        Sets the `number_of_slots` number of time slots
        to 'taken' starting at 'time'

        :param order_item:
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
            ts.order_item = order_item
            ts.save()

        next_index = first_slot_index + shift + 1
        if next_index == len(time_slots):
            return None

        return time_slots[next_index].value

# TODO referrals
# TODO feedbacks
