# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0039_auto_20150805_0953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filtervalue',
            name='filter_type',
            field=models.IntegerField(choices=[(5, 'Размер мужской одежды'), (3, 'Размер женской одежды'), (4, 'Размер обуви'), (2, 'Размер детской одежды'), (1, 'Цвет')], db_index=True),
        ),
        migrations.AlterField(
            model_name='filtervaluetoproducttype',
            name='filter_type',
            field=models.IntegerField(choices=[(5, 'Размер мужской одежды'), (3, 'Размер женской одежды'), (4, 'Размер обуви'), (2, 'Размер детской одежды'), (1, 'Цвет')], db_index=True),
        ),
    ]
