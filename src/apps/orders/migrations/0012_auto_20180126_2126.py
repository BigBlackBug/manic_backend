# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-26 21:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_order_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('CREATED', 'Создан'), ('ACTIVATED', 'Принят Мастером'), ('STARTED', 'Начат'), ('DONE', 'Завершён')], default='CREATED', max_length=10),
        ),
    ]