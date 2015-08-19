# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0019_auto_20150722_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.IntegerField(blank=True, db_index=True, verbose_name='Статус', choices=[(1, 'Проект'), (2, 'На согласовании'), (3, 'На доработке'), (4, 'Согласована'), (5, 'Действует'), (6, 'Приостановлена'), (7, 'Старт запланирован'), (8, 'Завершена'), (9, 'Отменена')], default=1),
        ),
    ]
