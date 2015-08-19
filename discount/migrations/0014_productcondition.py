# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0013_product_start_after_approve'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductCondition',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('condition', models.TextField(verbose_name='Условие')),
                ('product', models.ForeignKey(to='discount.Product', related_name='conditions')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
