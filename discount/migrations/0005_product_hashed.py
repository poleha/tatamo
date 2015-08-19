# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0004_shop_hashed'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='hashed',
            field=models.CharField(blank=True, max_length=40),
        ),
    ]
