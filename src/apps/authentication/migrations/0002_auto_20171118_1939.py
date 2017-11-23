# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-18 19:39
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('masters', '0010_feedback'),
        ('clients', '0005_address_comment'),
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='token',
            name='user',
        ),
        migrations.AddField(
            model_name='token',
            name='client',
            field=models.OneToOneField(default=None,
                                       on_delete=django.db.models.deletion.CASCADE,
                                       related_name='token',
                                       to='clients.Client', null=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='token',
            name='master',
            field=models.OneToOneField(default=None,
                                       on_delete=django.db.models.deletion.CASCADE,
                                       related_name='token',
                                       to='masters.Master', null=True),
            preserve_default=False,
        ),
    ]