# -*- coding: utf-8 -*-
import logging
import os

from django.db import models
from django.dispatch import receiver

from .models import ServiceCategory

logger = logging.getLogger(__name__)


# These two auto-delete files from filesystem when they are unneeded:
@receiver(models.signals.post_delete, sender=ServiceCategory)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `ServiceCategory` object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            logger.info(f'Removing image of category {instance.name}')
            os.remove(instance.image.path)


@receiver(models.signals.pre_save, sender=ServiceCategory)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `ServiceCategory` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = ServiceCategory.objects.get(pk=instance.pk).image
        # if there was no file associated with the category
        if not old_file:
            logger.info(f'No image was associated with '
                        f'category {instance.name}')
            return False
    except ServiceCategory.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            logger.info(f'Removing image of category {instance.name}')
            os.remove(old_file.path)
