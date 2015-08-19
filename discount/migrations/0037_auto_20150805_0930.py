# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0036_productstat_ip'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='simple_code',
            field=models.CharField(max_length=100, verbose_name='Код акции', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='use_code_postfix',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='product',
            name='use_simple_code',
            field=models.BooleanField(default=False),
        ),
    ]
