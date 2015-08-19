# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0032_auto_20150731_1422'),
    ]

    operations = [
        migrations.AddField(
            model_name='producttype',
            name='share_filter_params',
            field=models.BooleanField(default=False),
        ),
    ]
