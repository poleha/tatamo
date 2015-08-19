# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0025_auto_20150728_1914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filtervalue',
            name='title_int',
            field=models.PositiveIntegerField(default=0, blank=True, db_index=True),
        ),
        migrations.AlterIndexTogether(
            name='filtervalue',
            index_together=set([('title_int', 'title')]),
        ),
    ]
