# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-28 20:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(
                choices=[('CREATED', 'Создан'), ('ACCEPTED', 'Принят Мастером'),
                         ('DONE', 'Завершён')], default='CREATED',
                max_length=8),
        ),
    ]