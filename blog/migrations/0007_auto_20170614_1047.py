# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-14 02:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_auto_20170614_1041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='tag',
            field=models.ManyToManyField(blank=True, to='blog.Tag'),
        ),
    ]
