import random
from datetime import datetime
from datetime import timedelta as delta

from django.utils import timezone

from src.apps.authentication.models import PhoneAuthUser, Token
from src.apps.authentication.utils import Gender
from src.apps.categories.models import ServiceCategory, Service
from src.apps.clients.models import Address, Client
from src.apps.core import utils
from src.apps.masters.models import Master, Location, Schedule, TimeSlot
from src.apps.masters.receivers import *
from src.apps.orders.models import Order, OrderItem, OrderStatus


def make_category(category_name):
    category = ServiceCategory.objects.create(name=category_name,
                                              image=utils.make_in_memory_image(
                                                  'img'))

    service = Service.objects.create(category=category,
                                     name=category_name + ' обычный',
                                     description='d',
                                     cost=10,
                                     min_duration=30,
                                     max_duration=60)

    service = Service.objects.create(category=category,
                                     name=category_name + ' топовый',
                                     description='d',
                                     cost=100,
                                     min_duration=60,
                                     max_duration=90)
    return category


def make_master(name, lon):
    randstring = str(random.randint(1000, 2000))
    user = PhoneAuthUser.objects.create(phone=randstring)
    master = Master.objects.create(user=user, first_name=name,
                                   email=randstring + 'bigblackbugg@gmail.com',
                                   avatar=utils.make_in_memory_image(
                                       'supername'),
                                   gender=Gender.MALE,
                                   date_of_birth=timezone.now(),
                                   location=Location.objects.create(lat=10,
                                                                    lon=lon))
    return master


def make_token():
    token, _ = Token.objects.get_or_create(
        user=PhoneAuthUser.objects.create(phone='777'))
    return token


def make_client(user=None):
    if not user:
        user = PhoneAuthUser.objects.create(
            phone=str(random.randint(1000, 2000)))
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


def make_everything():
    # making an auth token
    vasya = make_master("VASYA", 11.0)
    petya = make_master("PETYA", 12.0)

    hands = make_category("Маникюр")
    feet = make_category("Педикюр")

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

    TimeSlot.objects.create(time=Time.objects.create(hour=16, minute=30),
                            taken=False, schedule=schedule)


def make_order(client, service, master, time, status=OrderStatus.CREATED,
               order_date=timezone.now().date()):
    order = Order.objects.create(client=client, date=order_date,
                                 time=time, status=status)
    schedule = master.get_schedule(order_date)
    slot = schedule.get_slot(time)

    order_item = OrderItem.objects.create(service=service,
                                          master=master,
                                          order=order,
                                          locked=False)
    slot.order_item = order_item
    slot.taken = True
    slot.save()
    return order, order_item


def make_order_services(client, services, master, order_time,
                        status=OrderStatus.CREATED, order_date=timezone.now()
                        .date(), locked=False):
    order = Order.objects.create(client=client, date=order_date,
                                 time=order_time, status=status)
    schedule = master.get_schedule(order_date)
    order_time = datetime.combine(timezone.now(), order_time)
    for service in services:
        slot = schedule.get_slot(order_time.time())
        order_item = OrderItem.objects.create(service=service,
                                              master=master,
                                              order=order,
                                              locked=locked)
        slot.order_item = order_item
        slot.save()
        order_time += delta(minutes=TimeSlot.DURATION)
    return order


def _make_time(hour: int, minute: int) -> Time:
    return Time(hour=hour, minute=minute,
                value=time(hour=hour, minute=minute))
