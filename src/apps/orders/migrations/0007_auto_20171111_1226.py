# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-11 12:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_auto_20171110_1918'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='locked',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('CREATED', 'Создан'), ('ACCEPTED', 'Принят Мастером'), ('STARTED', 'Начат'), ('DONE', 'Завершён')], default='CREATED', max_length=8),
        ),
    ]
