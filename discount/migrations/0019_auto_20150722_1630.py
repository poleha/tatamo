# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0018_auto_20150722_1335'),
    ]

    operations = [
        migrations.AddField(
            model_name='productchanger',
            name='normal_price',
            field=models.IntegerField(verbose_name='Цена до акции', db_index=True, default=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productchanger',
            name='stock_price',
            field=models.IntegerField(verbose_name='Цена по акции', db_index=True, default=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='link',
            field=models.CharField(verbose_name='Ссылка на страницу товара на сайте магазина', blank=True, max_length=4000),
        ),
        migrations.AlterField(
            model_name='productchanger',
            name='link',
            field=models.CharField(verbose_name='Ссылка на страницу товара на сайте магазина', blank=True, max_length=4000),
        ),
    ]
