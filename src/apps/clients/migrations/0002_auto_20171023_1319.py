# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-23 13:19
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='address',
            field=models.OneToOneField(blank=True, null=True,
                                       on_delete=django.db.models.deletion.CASCADE,
                                       related_name='client',
                                       to='clients.Address'),
        ),
        migrations.AddField(
            model_name='client',
            name='device',
            field=models.OneToOneField(null=True,
                                       on_delete=django.db.models.deletion.SET_NULL,
                                       related_name='client',
                                       related_query_name='client',
                                       to='devices.FCMDevice'),
        ),
    ]
