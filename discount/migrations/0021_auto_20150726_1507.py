# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0020_auto_20150723_1312'),
    ]

    operations = [
        migrations.AddField(
            model_name='producttocart',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2015, 7, 26, 12, 7, 15, 738898, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='producttocart',
            name='subscription_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
