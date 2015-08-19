# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0035_productstat'),
    ]

    operations = [
        migrations.AddField(
            model_name='productstat',
            name='ip',
            field=models.CharField(max_length=15, default=''),
            preserve_default=False,
        ),
    ]
