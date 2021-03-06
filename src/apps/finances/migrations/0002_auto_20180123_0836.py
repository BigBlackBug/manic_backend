# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-23 08:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactionentry',
            name='master',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='masters.Master'),
        ),
        migrations.AlterField(
            model_name='transactionentry',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='orders.Order'),
        ),
    ]
