# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-19 06:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0010_auto_20171124_0945'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='comment',
            field=models.CharField(blank=True, max_length=1024),
        ),
    ]