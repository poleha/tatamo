# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0031_auto_20150730_0915'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='brand',
            options={'ordering': ['title']},
        ),
        migrations.AlterModelOptions(
            name='shop',
            options={'ordering': ['title']},
        ),
    ]
