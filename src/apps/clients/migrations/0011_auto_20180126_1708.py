# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-26 17:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0010_address_last_used_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, unique=True)),
                ('content', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='client',
            name='device',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='client', related_query_name='client', to='devices.FCMDevice'),
        ),
        migrations.AddField(
            model_name='complaint',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='complaints', to='clients.Client'),
        ),
    ]
