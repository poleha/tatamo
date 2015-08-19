# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0012_auto_20150709_1729'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='start_after_approve',
            field=models.BooleanField(verbose_name='Стартовать/запланировать акцию автоматически после согласования', default=True),
        ),
    ]
