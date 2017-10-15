# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-09 20:49
from __future__ import unicode_literals

import django.contrib.postgres.fields.hstore
from django.contrib.postgres.operations import HStoreExtension
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('categories', '0001_initial'),
        ('masters', '0001_initial'),
        ('clients', '0001_initial'),
    ]

    operations = [
        HStoreExtension(),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('special', django.contrib.postgres.fields.hstore.HStoreField(blank=True, null=True)),
                ('client', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='clients.Client')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('master', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='masters.Master')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='orders.Order')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='categories.Service')),
            ],
        ),
    ]
