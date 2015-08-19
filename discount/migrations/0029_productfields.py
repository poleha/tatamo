# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0028_auto_20150728_1939'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductFields',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('weight', models.PositiveIntegerField(db_index=True, default=0)),
                ('product', models.ForeignKey(to='discount.Product', related_name='fields')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
