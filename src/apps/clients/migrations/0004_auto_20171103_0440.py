# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-03 04:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0003_paymentcard'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='address',
        ),
        migrations.AddField(
            model_name='address',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='clients.Client'),
        ),
        migrations.AddField(
            model_name='address',
            name='is_default',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
