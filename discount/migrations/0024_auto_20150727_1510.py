# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0023_auto_20150727_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relatedproduct',
            name='product',
            field=models.ForeignKey(to='discount.Product', verbose_name='Акция', related_name='related_products'),
        ),
        migrations.AlterField(
            model_name='relatedproduct',
            name='related_product',
            field=models.ForeignKey(to='discount.Product', verbose_name='Связанная акция', related_name='products'),
        ),
    ]
