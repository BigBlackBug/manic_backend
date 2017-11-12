import os
import random
from datetime import timedelta as delta

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.apps.authentication.models import PhoneAuthUser, Token
from src.apps.authentication.utils import Gender
from src.apps.categories.models import ServiceCategory, Service, DisplayItem
from src.apps.clients.models import Client, Address
from src.apps.core import utils
from src.apps.masters.models import Master, Location, Schedule, TimeSlot
from src.apps.masters.receivers import *
# TODO unify this and data creation for tests
from src.apps.orders.models import OrderStatus, Order, OrderItem


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

    token, _ = Token.objects.get_or_create(user=vasya.user,
                                           key='master_token')

    for service in feet.services.all():
        petya.services.add(service)
    petya.save()

    # VASYA works on -2, 0,+1, does manicure, got three slots
    schedule = Schedule.objects.create(master=vasya, date=utils.get_date(-2))
    schedule.save()

    TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=00),
                            taken=False, schedule=schedule)
    TimeSlot.objects.create(time=Time.objects.create(hour=11, minute=30),
                            taken=False, schedule=schedule)

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

    client = make_client()
    token, _ = Token.objects.get_or_create(user=client.user,
                                           key='client_token')

    order, _ = make_order(client=client, service=hands.services.all()[0],
                          master=vasya, order_time='11:00')
    order, _ = make_order(client=client, service=hands.services.all()[1],
                          master=vasya, order_time='12:00')

    order, _ = make_order(client=client, service=hands.services.all()[0],
                          master=vasya, order_time='11:00',
                          order_date=utils.get_date(-2),
                          status=OrderStatus.DONE)


def make_order(client, service, master, order_time, status=OrderStatus.CREATED,
               order_date=timezone.now().date()):
    order = Order.objects.create(client=client, date=order_date,
                                 time=order_time, status=status)
    schedule = master.get_schedule(order_date)
    slot = schedule.get_slot(order_time)

    order_item = OrderItem.objects.create(service=service,
                                          master=master,
                                          order=order,
                                          locked=False)
    slot.order_item = order_item
    slot.save()
    return order, order_item


def make_client(user=None):
    if not user:
        user = PhoneAuthUser.objects.create(phone='88005553535')
    client = Client.objects.create(user=user, first_name='client',
                                   avatar=utils.make_in_memory_image(
                                       'supername'),
                                   gender=Gender.MALE,
                                   date_of_birth=timezone.now())
    Address.objects.create(
        location=Location.objects.create(lat=10,
                                         lon=10),
        city='kazan', street_name='latstr',
        building='4', floor=2, apt_number=79,
        entrance=6, has_intercom=True, client=client,
        is_default=True)
    return client


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
