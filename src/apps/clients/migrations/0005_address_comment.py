# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-03 05:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0004_auto_20171103_0440'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='comment',
            field=models.CharField(blank=True, max_length=1024),
        ),
    ]
