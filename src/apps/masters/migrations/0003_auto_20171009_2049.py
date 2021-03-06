# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-09 20:49
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('orders', '0001_initial'),
        ('categories', '0001_initial'),
        ('masters', '0002_time_instance_creation'),
        ('authentication', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='master',
            name='device',
            field=models.OneToOneField(null=True,
                                       on_delete=django.db.models.deletion.SET_NULL,
                                       related_name='master',
                                       related_query_name='master',
                                       to='devices.FCMDevice'),
        ),
        migrations.AddField(
            model_name='timeslot',
            name='order_item',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    to='orders.OrderItem'),
        ),
        migrations.AddField(
            model_name='timeslot',
            name='schedule',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='time_slots',
                                    to='masters.Schedule'),
        ),
        migrations.AddField(
            model_name='timeslot',
            name='time',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='+', to='masters.Time'),
        ),
        migrations.AddField(
            model_name='schedule',
            name='master',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='schedule',
                                    to='masters.Master'),
        ),
        migrations.AddField(
            model_name='portfolioimage',
            name='master',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='portfolio',
                                    to='masters.Master'),
        ),
        migrations.AddField(
            model_name='master',
            name='location',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, related_name='+',
                to='core.Location'),
        ),
        migrations.AddField(
            model_name='master',
            name='services',
            field=models.ManyToManyField(related_name='masters',
                                         to='categories.Service'),
        ),
        migrations.AddField(
            model_name='master',
            name='user',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='master', related_query_name='master',
                to='authentication.PhoneAuthUser'),
        ),
    ]
