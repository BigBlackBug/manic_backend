# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-20 00:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0009_address_creation_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='last_used_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]