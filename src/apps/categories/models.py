# -*- coding: utf-8 -*-
import uuid

from django.db import models


def make_id(instance, filename):
    return 'categories/' + str(uuid.uuid4())


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
    image = models.ImageField(upload_to=make_id, blank=True)

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
    duration = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.name} from category {self.category.name}'
