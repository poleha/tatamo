# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0003_auto_20150701_2030'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='hashed',
            field=models.CharField(blank=True, max_length=40),
        ),
    ]
