# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-14 07:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0006_auto_20171111_0812'),
    ]

    operations = [
        migrations.AddField(
            model_name='master',
            name='email',
            field=models.EmailField(default='email@mail.com', max_length=254),
            preserve_default=False,
        ),
    ]
