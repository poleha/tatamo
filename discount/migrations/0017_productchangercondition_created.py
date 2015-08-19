# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0016_auto_20150720_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='productchangercondition',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 20, 16, 21, 25, 136784, tzinfo=utc), auto_now_add=True, db_index=True),
            preserve_default=False,
        ),
    ]
