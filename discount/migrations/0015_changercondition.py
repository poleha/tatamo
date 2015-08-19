# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0014_productcondition'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChangerCondition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('condition', models.TextField(verbose_name='Условие')),
                ('product_changer', models.ForeignKey(to='discount.ProductChanger', related_name='conditions')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
