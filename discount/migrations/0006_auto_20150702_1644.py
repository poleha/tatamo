# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0005_product_hashed'),
    ]

    operations = [
        migrations.RenameField(
            model_name='filtervaluetoproducttype',
            old_name='filter_param',
            new_name='filter_type',
        ),
    ]
