# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2018-01-01 23:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client_kakao', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='request',
            name='session_id',
        ),
        migrations.AddField(
            model_name='request',
            name='user_key',
            field=models.CharField(default=b'unknown', max_length=20),
        ),
    ]