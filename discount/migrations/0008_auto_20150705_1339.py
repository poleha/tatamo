# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0007_auto_20150702_2044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.IntegerField(db_index=True, verbose_name='Статус', blank=True, choices=[(1, 'Проект'), (2, 'На согласовании'), (3, 'На доработке'), (4, 'Согласована'), (5, 'Действует'), (6, 'Приостановлена'), (7, 'Ожидает старта'), (8, 'Завершена'), (9, 'Отменена')], default=1),
        ),
    ]
