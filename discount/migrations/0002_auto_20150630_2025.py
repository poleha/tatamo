# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shop',
            name='work_time',
            field=models.TextField(verbose_name='Время работы', blank=True, default=''),
        ),
    ]
