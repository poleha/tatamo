# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0009_auto_20150705_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='role',
            field=models.PositiveIntegerField(choices=[(1, 'Пользователь'), (2, 'Менеджер магазина'), (3, 'Менеджер Татамо')], default=1, blank=True),
        ),
    ]
