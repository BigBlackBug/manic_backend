# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-25 16:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0005_auto_20180123_0000'),
    ]

    operations = [
        migrations.AddField(
            model_name='displayitem',
            name='priority',
            field=models.IntegerField(default=0),
        ),
    ]
