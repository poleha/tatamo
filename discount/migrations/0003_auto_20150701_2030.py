# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0002_auto_20150630_2025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shopstousers',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Имя пользователя'),
        ),
    ]
