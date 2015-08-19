# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0030_auto_20150729_1812'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productfields',
            name='product',
            field=models.OneToOneField(to='discount.Product', related_name='product_fields'),
        ),
    ]
