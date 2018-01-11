import random
from datetime import datetime
from datetime import timedelta as delta

from django.utils import timezone

from src.apps.authentication.models import PhoneAuthUser, Token
from src.apps.authentication.utils import Gender
from src.apps.categories.models import ServiceCategory, Service, DisplayItem
from src.apps.clients.models import Address, Client, ClientStatus, PaymentCard
from src.apps.core import utils
from src.apps.masters.models import Master, Location, Schedule, TimeSlot, \
    MasterStatus, PortfolioImage, PortfolioImageStatus, Balance
from src.apps.masters.receivers import *
from src.apps.orders.models import Order, OrderItem, OrderStatus, PaymentType


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


def make_category(category_name):
    category = ServiceCategory.objects.create(name=category_name,
                                              image=utils.make_in_memory_image(
                                                  'img'))

    Service.objects.create(category=category,
                           name=category_name + ' обычный',
                           description='d',
                           cost=random.randint(10, 90),
                           min_duration=30,
                           max_duration=60)

    Service.objects.create(category=category,
                           name=category_name + ' топовый',
                           description='d',
                           cost=random.randint(10, 90),
                           min_duration=60,
                           max_duration=90)
    return category


def make_master(name, lon, user=None, activated=True,
                about='awesome master!', make_portfolio=True,
                make_balance=False):
    def _rand():
        random.seed()
        return random.randint(100000, 200000)

    if not user:
        user = PhoneAuthUser.objects.create(phone=str(_rand()))
    if activated:
        master = Master.objects.create(
            user=user, first_name=name,
            about=about,
            email=str(_rand()) + 'bigblackbugg@gmail.com',
            avatar=utils.make_in_memory_image('supername'),
            status=MasterStatus.VERIFIED,
            gender=Gender.MALE,
            date_of_birth=timezone.now(),
            location=Location.objects.create(lat=10, lon=lon))
        if make_portfolio:
            PortfolioImage.objects.create(
                image=utils.make_in_memory_image('heyho'),
                description=str(_rand()) + 'description',
                status=PortfolioImageStatus.ON_MODERATION,
                master=master)
        if make_balance:
            Balance.objects.create(master=master, future=_rand(),
                                   on_hold=_rand(), transferred=_rand())
        else:
            Balance.objects.create(master=master)

    else:
        master = Master.objects.create(user=user, status=MasterStatus.DUMMY)

    return master


def make_token(client=None, master=None):
    if client:
        token, _ = Token.objects.get_or_create(
            client=client)
    elif master:
        token, _ = Token.objects.get_or_create(
            master=master)
    else:
        raise ValueError('provide either client or master')
    return token


def make_client(user=None, first_name='client', activated=True, make_card=True):
    if not user:
        user = PhoneAuthUser.objects.create(
            phone=str(random.randint(1, 2000000)))
    if activated:
        client = Client.objects.create(user=user, first_name=first_name,
                                       status=ClientStatus.VERIFIED,
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
        if make_card:
            PaymentCard.objects.create(client=client, cryptogram='BLABL',
                                       client_name_on_card='JOHN',
                                       card_number='190')
    else:
        client = Client.objects.create(user=user,
                                       status=ClientStatus.DUMMY)
    return client


def make_everything():
    # making an auth token
    vasya = make_master("VASYA", 11.0, about='a terrible master')
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


def make_order(client, service, master, order_time, status=OrderStatus.ACCEPTED,
               order_date=timezone.now().date(), payment_type=PaymentType.CARD,
               comment=''):
    order = Order.objects.create(client=client, date=order_date,
                                 time=order_time, status=status,
                                 payment_type=payment_type,
                                 comment=comment)
    schedule = master.get_schedule(order_date)
    slot = schedule.get_slot(order_time)

    order_item = OrderItem.objects.create(service=service,
                                          master=master,
                                          order=order,
                                          locked=False)
    master.create_order_payment(order, order_item)
    slot.order_item = order_item
    slot.taken = True
    slot.save()
    return order, order_item


def make_order_services(client, services, master, order_time,
                        status=OrderStatus.ACCEPTED,
                        order_date=timezone.now().date(),
                        payment_type=PaymentType.CARD, locked=False):
    order = Order.objects.create(client=client, date=order_date,
                                 time=order_time, status=status,
                                 payment_type=payment_type)
    schedule = master.get_schedule(order_date)
    order_time = datetime.combine(timezone.now(), order_time)
    for service in services:
        slot = schedule.get_slot(order_time.time())
        order_item = OrderItem.objects.create(service=service,
                                              master=master,
                                              order=order,
                                              locked=locked)
        master.create_order_payment(order, order_item)
        slot.order_item = order_item
        slot.save()
        order_time += delta(minutes=TimeSlot.DURATION)
    return order


def _make_time(hour: int, minute: int) -> Time:
    return Time(hour=hour, minute=minute,
                value=time(hour=hour, minute=minute))
