# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0037_auto_20150805_0930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='simple_code',
            field=models.CharField(verbose_name='Код акции', blank=True, max_length=100),
        ),
    ]
