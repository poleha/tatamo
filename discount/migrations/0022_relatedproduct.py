# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0021_auto_20150726_1507'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelatedProduct',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('product', models.ForeignKey(to='discount.Product', verbose_name='Акция', related_name='parent_products')),
                ('related_product', models.ForeignKey(to='discount.Product', verbose_name='Связанная акция', related_name='related_products')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
