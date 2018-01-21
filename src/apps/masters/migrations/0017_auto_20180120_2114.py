# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-20 21:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0016_balance_debt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='master',
            name='device',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='master', related_query_name='master', to='devices.FCMDevice'),
        ),
    ]