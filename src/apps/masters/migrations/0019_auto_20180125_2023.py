# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-25 20:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_order_comment'),
        ('masters', '0018_feedback_added'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='order',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='feedback', to='orders.Order'),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='master',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='masters.Master'),
        ),
    ]
