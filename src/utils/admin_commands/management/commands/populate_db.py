import os
import random
from datetime import timedelta as delta

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.apps.authentication.models import PhoneAuthUser
from src.apps.authentication.utils import Gender
from src.apps.categories.models import ServiceCategory, Service, DisplayItem
from src.apps.core import utils
from src.apps.masters.models import Master, Location, Schedule, TimeSlot
from src.apps.masters.receivers import *


# TODO unify this and data creation for tests
def make_master(name, lon, about='awesome master!'):
    user = PhoneAuthUser.objects.create(phone=str(random.randint(1000, 2000)))
    master = Master.objects.create(user=user, first_name=name,
                                   avatar=utils.make_in_memory_image(
                                       'supername'),
                                   gender=Gender.MALE,
                                   date_of_birth=timezone.now(),
                                   about=about,
                                   location=Location.objects.create(lat=10,
                                                                    lon=lon))
    return master


def make_display_item(*categories, name=None, special=None):
    if len(categories) == 1:
        di = DisplayItem.objects.create()
        di.categories.add(categories[0])
    else:
        di = DisplayItem.objects.create(name=name,
                                        image=utils.make_in_memory_image(
                                            'supername'),
                                        special=special and {
                                            'type': 'composite'})
        for category in categories:
            di.categories.add(category)
    return di


def make_everything():
    # making an auth token
    vasya = make_master("VASYA", 11.0, about='a terrible master')
    petya = make_master("PETYA", 12.0)

    hands = make_category("Маникюр")
    feet = make_category("Педикюр")

    make_display_item(hands)
    make_display_item(feet)
    make_display_item(hands, feet, name='4hands', special=True)

    for service in hands.services.all():
        vasya.services.add(service)
    vasya.save()

    for service in feet.services.all():
        petya.services.add(service)
    petya.save()

    # VASYA works on 0,+1, does manicure, got three slots
    schedule = Schedule.objects.create(master=vasya, date=timezone.now())
    schedule.save()

    TimeSlot.objects.create(time=Time.objects.create(hour=10, minute=30),
                            taken=True, schedule=schedule)
    TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=00),
                            taken=False, schedule=schedule)
    TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=30),
                            taken=False, schedule=schedule)
    TimeSlot.objects.create(time=Time.objects.create(hour=12, minute=00),
                            taken=False, schedule=schedule)

    schedule = Schedule.objects.create(master=vasya,
                                       date=timezone.now() + delta(days=1))
    schedule.save()

    TimeSlot.objects.create(time=Time.objects.create(hour=12, minute=30),
                            taken=False, schedule=schedule)
    TimeSlot.objects.create(time=Time.objects.create(hour=13, minute=00),
                            taken=False, schedule=schedule)
    TimeSlot.objects.create(time=Time.objects.create(hour=13, minute=30),
                            taken=False, schedule=schedule)

    # PETYA works on +2th, +3th does pedicure, got all slots on +2, none on +3
    schedule = Schedule.objects.create(master=petya,
                                       date=timezone.now() + delta(days=2))
    schedule.save()

    TimeSlot.objects.create(time=Time.objects.create(hour=10, minute=30),
                            taken=False, schedule=schedule)
    TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=00),
                            taken=False, schedule=schedule)
    TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=30),
                            taken=False, schedule=schedule)
    TimeSlot.objects.create(time=Time.objects.create(hour=12, minute=30),
                            taken=True, schedule=schedule)

    schedule = Schedule.objects.create(master=petya,
                                       date=timezone.now() + delta(days=3))
    schedule.save()


def make_category(category_name):
    category = ServiceCategory.objects.create(name=category_name,
                                              image=utils.make_in_memory_image(
                                                  'img'))

    Service.objects.create(category=category, name=category_name + ' обычный',
                           description='d',
                           cost=10,
                           min_duration=30,
                           max_duration=60)

    Service.objects.create(category=category, name=category_name + ' топовый',
                           description='d',
                           cost=100,
                           min_duration=60,
                           max_duration=90)
    return category


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def handle(self, *args, **options):
        settings = os.environ.get('DJANGO_SETTINGS_MODULE', None)
        if settings and ('dev' in settings or 'local' in settings):
            make_everything()
            print("aww yiss")
        else:
            print(f'you are not allowed to run this command: {settings}')
