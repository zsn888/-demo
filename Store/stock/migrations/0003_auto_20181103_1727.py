# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-11-03 17:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0002_auto_20181103_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fruit',
            name='name',
            field=models.CharField(max_length=32, unique=True),
        ),
    ]
