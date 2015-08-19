# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0033_producttype_share_filter_params'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producttocart',
            name='status',
            field=models.IntegerField(choices=[(1, 'В корзине'), (2, 'Код получен'), (3, 'Завершена магазином'), (4, 'Купил(а)'), (5, 'Передумал(а)'), (6, 'Для немедленного добавления'), (7, 'Приостановлена магазином'), (8, 'Удалена')], db_index=True, default=1),
        ),
    ]
