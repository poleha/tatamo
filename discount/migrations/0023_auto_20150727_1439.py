# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0022_relatedproduct'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relatedproduct',
            name='product',
            field=models.ForeignKey(verbose_name='Акция', related_name='products', to='discount.Product'),
        ),
    ]
