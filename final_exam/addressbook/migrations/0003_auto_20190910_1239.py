# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-09-10 04:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('addressbook', '0002_contact_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='contact_number',
            field=models.CharField(max_length=13),
        ),
    ]
