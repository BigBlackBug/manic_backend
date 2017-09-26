# -*- coding: utf-8 -*-
from datetime import time

from django.db import models
from django.dispatch import receiver

from .models import Time


@receiver(models.signals.pre_save, sender=Time)
def add_time_value(sender, instance, **kwargs):
    """
    Adds a 'value' TimeField to the Time instance
    """
    instance.value = time(hour=instance.hour, minute=instance.minute)
