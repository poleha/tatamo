# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discount', '0015_changercondition'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductChangerCondition',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('condition', models.TextField(verbose_name='Условие')),
                ('product_changer', models.ForeignKey(related_name='conditions', to='discount.ProductChanger')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='changercondition',
            name='product_changer',
        ),
        migrations.DeleteModel(
            name='ChangerCondition',
        ),
    ]
