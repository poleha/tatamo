# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0026_auto_20150728_1915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filtervalue',
            name='title_int',
            field=models.FloatField(blank=True, default=0, db_index=True),
        ),
    ]
