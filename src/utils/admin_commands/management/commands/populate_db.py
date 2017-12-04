import os
from datetime import timedelta as delta

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.apps.authentication.mgmt.models import AdminToken
from src.apps.authentication.models import Token as AppToken
from src.apps.authentication.utils import get_admin_user_model
from src.apps.core import utils
from src.apps.masters.models import Schedule, TimeSlot
from src.apps.masters.receivers import *
from src.apps.orders.models import OrderStatus
from src.utils.object_creation import make_order, make_client, make_master, \
    make_category, make_display_item


def _make_everything():
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

    token, _ = AppToken.objects.get_or_create(master=vasya,
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
                            taken=False, schedule=schedule)
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
                            taken=False, schedule=schedule)

    schedule = Schedule.objects.create(master=petya,
                                       date=timezone.now() + delta(days=3))
    schedule.save()

    client = make_client()
    token, _ = AppToken.objects.get_or_create(client=client,
                                              key='client_token')

    order, _ = make_order(client=client, service=hands.services.all()[0],
                          master=vasya, order_time='10:30')
    order, _ = make_order(client=client, service=hands.services.all()[1],
                          master=vasya, order_time='11:00')
    # still got 2 slots on the first day

    order, _ = make_order(client=client, service=hands.services.all()[0],
                          master=vasya, order_time='11:00',
                          order_date=utils.get_date(-2),
                          status=OrderStatus.DONE)


def _make_admin_token():
    user = get_admin_user_model().objects.create(username='korch')
    user.set_password('korch')
    user.save()
    return AdminToken.objects.create(user=user, key='korchagin_token')


class Command(BaseCommand):
    def handle(self, *args, **options):
        settings = os.environ.get('DJANGO_SETTINGS_MODULE', None)
        if settings and ('dev' in settings or 'local' in settings):
            _make_everything()
            _make_admin_token()
            print("aww yiss")
        else:
            print(f'you are not allowed to run this command: {settings}')
