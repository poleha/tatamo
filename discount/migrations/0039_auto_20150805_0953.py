# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0038_auto_20150805_0930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='use_code_postfix',
            field=models.BooleanField(verbose_name='Использовать постфикс для промокода', default=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='use_simple_code',
            field=models.BooleanField(verbose_name='Сгенерировать промокод вручную', default=False),
        ),
    ]
