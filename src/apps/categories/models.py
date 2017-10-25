# -*- coding: utf-8 -*-
from django.contrib.postgres.fields import HStoreField
from django.db import models

from src.apps.core.utils import Folders


# TODO WHAT A BUG. Categories don't delete images!!!!

class ServiceCategory(models.Model):
    """
    A category for a number of services

    *foreign key fields*

    `services`
    """
    # FK fields
    # services
    name = models.CharField(max_length=64)
    # TODO what about file extensions?
    image = models.ImageField(upload_to=Folders.categories, blank=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    """
    A service that a master can provide
    *foreign key fields*

    `masters`
    """

    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE,
                                 related_name='services')

    name = models.CharField(max_length=64)
    description = models.CharField(max_length=256)

    # roubles
    cost = models.PositiveIntegerField()

    # in minutes
    min_duration = models.PositiveIntegerField()
    max_duration = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.name} from category {self.category.id}'


class DisplayItem(models.Model):
    """
    A wrapper entity around ServiceCategory, which is displayed
    on the Category screen
    """
    name = models.CharField(max_length=64, null=True)
    image = models.ImageField(upload_to=Folders.display_items, null=True)
    categories = models.ManyToManyField(ServiceCategory, related_name='+')
    special = HStoreField(null=True)

    def __str__(self):
        if not self.name:
            return 'Unnamed parent item'
        return f'{self.name}'
