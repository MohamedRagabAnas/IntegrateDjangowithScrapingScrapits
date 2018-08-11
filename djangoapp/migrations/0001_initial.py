# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-08 12:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('court', models.CharField(max_length=60)),
                ('description', models.CharField(max_length=1024)),
            ],
        ),
    ]
