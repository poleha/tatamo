# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0029_productfields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productfields',
            name='product',
            field=models.OneToOneField(to='discount.Product', related_name='fields'),
        ),
    ]
